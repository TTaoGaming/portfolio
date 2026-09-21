// Independent exact-integer verifier using Boost.Multiprecision; C++17.
// This intentionally does not import generator or Python/JavaScript code.
#include <boost/multiprecision/cpp_int.hpp>
#include <fstream>
#include <iostream>
#include <regex>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
using boost::multiprecision::cpp_int;
int main(int argc,char**argv) {
  try {
    if(argc!=2) throw std::runtime_error("usage: verify_cpp certificate.txt");
    std::ifstream f(argv[1],std::ios::binary);
    if(!f) throw std::runtime_error("cannot open file");
    std::string all((std::istreambuf_iterator<char>(f)),std::istreambuf_iterator<char>());
    if(all.empty()||all.size()>512000||all.back()!='\n') throw std::runtime_error("size/newline");
    const cpp_int n("0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973");
    std::set<cpp_int> known; known.insert(cpp_int(1));
    std::regex grammar("[1-9][0-9]{0,119} [1-9][0-9]{0,119} [1-9][0-9]{0,119}");
    std::istringstream stream(all); std::string line; cpp_int last=1;
    unsigned count=0,squares=0;
    while(std::getline(stream,line)) {
      if(++count>1024) throw std::runtime_error("operation limit");
      if(!std::regex_match(line,grammar)) throw std::runtime_error("invalid decimal row");
      std::istringstream row(line); std::string cs,as,bs; row>>cs>>as>>bs;
      cpp_int c(cs),a(as),b(bs);
      if(!known.count(a)||!known.count(b)) throw std::runtime_error("unavailable parent");
      if(known.count(c)) throw std::runtime_error("duplicate output");
      if(a+b!=c) throw std::runtime_error("incorrect sum");
      known.insert(c); if(a==b)++squares; last=c;
    }
    if(last!=n-2) throw std::runtime_error("incorrect scalar-inversion exponent");
    std::cout<<"{\"valid\":true,\"operations\":"<<count<<",\"squarings\":"<<squares
      <<",\"multiplications\":"<<(count-squares)<<",\"endpoint_hex\":\""<<std::hex<<last<<"\"}\n";
    return 0;
  } catch(const std::exception&e) {
    std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;
  }
}
