"""Inject a test-only paired benchmark into ring@840167e with the 422 patch applied.

The baseline function is read from the pinned Git commit; the candidate is the
already-applied patch. The test calls both in the same release binary.
"""
import pathlib
import subprocess

src = pathlib.Path("src/ec/suite_b/ops/p384.rs")
base = subprocess.check_output(["git", "show", "HEAD:src/ec/suite_b/ops/p384.rs"], text=True)
patched = src.read_text()
start = "fn p384_scalar_inv_to_mont(a: Scalar<R>, cpu: cpu::Features) -> Scalar<R> {"
end = '\nunsafe extern "C" fn p384_elem_sqr_mont('
assert base.count(start) == patched.count(start) == 1
old_fn = base[base.index(start):base.index(end)].replace(
    "fn p384_scalar_inv_to_mont(", "fn p384_scalar_inv_baseline(", 1
)
assert "fn p384_scalar_inv_baseline(" not in patched
patched = patched.replace(start, "#[inline(never)]\n" + old_fn + "\n#[inline(never)]\n" + start, 1)
patched += r'''

#[cfg(test)]
mod independent_p384_speed {
    extern crate std;
    use super::*;
    use std::hint::black_box;
    use std::time::Instant;

    fn time_one(f: fn(Scalar<R>, cpu::Features) -> Scalar<R>, a: Scalar<R>,
                cpu: cpu::Features, reps: usize) -> u128 {
        let t = Instant::now();
        for _ in 0..reps {
            let _ = black_box(f(black_box(a), cpu));
        }
        t.elapsed().as_nanos()
    }

    #[test]
    fn paired_scalar_inversion() {
        let cpu = cpu::features();
        let mut raw = Scalar::one();
        raw.limbs[0] = 7;
        let input = PRIVATE_SCALAR_OPS.to_mont(&raw, cpu);
        let old = p384_scalar_inv_baseline(input, cpu);
        let new = p384_scalar_inv_to_mont(input, cpu);
        assert_eq!(old.limbs, new.limbs);

        let reps = 1000;
        let _ = time_one(p384_scalar_inv_baseline, input, cpu, reps);
        let _ = time_one(p384_scalar_inv_to_mont, input, cpu, reps);
        for i in 0..40 {
            let (baseline, candidate) = if i % 2 == 0 {
                (time_one(p384_scalar_inv_baseline, input, cpu, reps),
                 time_one(p384_scalar_inv_to_mont, input, cpu, reps))
            } else {
                let candidate = time_one(p384_scalar_inv_to_mont, input, cpu, reps);
                let baseline = time_one(p384_scalar_inv_baseline, input, cpu, reps);
                (baseline, candidate)
            };
            std::println!("HFO_PAIR,{i},{baseline},{candidate},{reps}");
        }
    }
}
'''
src.write_text(patched)
print({"baseline_bytes": len(old_fn.encode()), "patched_bytes": src.stat().st_size})
