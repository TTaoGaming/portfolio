#include <boost/multiprecision/cpp_int.hpp>
#include <iostream>
#include <set>
#include <stdexcept>
#include <tuple>
#include <vector>
#include <map>
using boost::multiprecision::cpp_int;
static cpp_int H(const std::string&s){cpp_int x=0;for(char c:s){int v=(c>='0'&&c<='9')?c-'0':(c>='A'&&c<='F')?c-'A'+10:c-'a'+10;x=(x<<4)+v;}return x;}
int main(){cpp_int N=H("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973"),TARGET=N-2;std::vector<std::pair<cpp_int,cpp_int>> P={{1,1},{2,1},{3,3},{6,6},{12,12},{24,24},{48,48},{96,96},{192,3},{195,195},{390,390},{780,780},{1560,3},{1563,192},{1755,192},{1755,780},{2535,2},{2535,1560}};std::map<int,cpp_int>T={{186,1},{181,1563},{167,1563},{162,4095},{151,2535},{148,4095},{141,1563},{135,1947},{132,1},{123,2537},{115,3},{112,4095},{103,1563},{94,195},{86,1563},{78,1947},{72,2535},{60,1947},{53,2535},{50,3},{34,1563},{29,1755},{25,4095},{23,1755},{13,2537},{7,4095},{3,1},{0,2537}};std::set<cpp_int>seen{1};std::vector<std::tuple<cpp_int,cpp_int,cpp_int>> rows;auto add=[&](cpp_int a,cpp_int b){if(!seen.count(a)||!seen.count(b))throw std::runtime_error("parent");cpp_int o=a+b;if(seen.count(o)||!(a<o&&b<o))throw std::runtime_error("order");rows.push_back({o,a,b});seen.insert(o);return o;};for(auto [a,b]:P)add(a,b);cpp_int x=4095;for(int sh:{12,24,48,96}){cpp_int base=x;for(int i=0;i<sh;i++)x=add(x,x);x=add(x,base);}if(x!=(cpp_int(1)<<192)-1)throw std::runtime_error("M192");for(int pos=191;pos>=0;--pos){x=add(x,x);auto it=T.find(pos);if(it!=T.end())x=add(x,it->second);}std::set<cpp_int>s2{1};cpp_int prev=1;int S=0,M=0;for(auto [o,a,b]:rows){if(!s2.count(a)||!s2.count(b)||o!=a+b||!(o>prev&&a<o&&b<o))throw std::runtime_error("chain");if(a==b)S++;else M++;s2.insert(o);prev=o;}if(prev!=TARGET||rows.size()!=422||S!=382||M!=40)throw std::runtime_error("final/count");std::cout<<"PASS "<<rows.size()<<" "<<S<<"S "<<M<<"M\n";}
