#include <bits/stdc++.h>
using namespace std;
struct Pt{int x,y;};
struct Key{int A,B,C; bool operator<(Key const&o)const{return tie(A,B,C)<tie(o.A,o.B,o.C);} };
int gcd3(int a,int b,int c){return std::gcd(std::gcd(abs(a),abs(b)),abs(c));}
Key lineKey(Pt p, Pt q){int A=q.y-p.y, B=p.x-q.x, C=-(A*p.x+B*p.y); int g=gcd3(A,B,C); A/=g;B/=g;C/=g; if(A<0||(A==0&&B<0)){A=-A;B=-B;C=-C;} return {A,B,C};}
int main(int argc,char**argv){
 int N=20,K=31,par=0,TL=60,seed=1; if(argc>1)N=atoi(argv[1]); if(argc>2)K=atoi(argv[2]); if(argc>3)TL=atoi(argv[3]); if(argc>4)seed=atoi(argv[4]); if(argc>5)par=atoi(argv[5]);
 mt19937 rng(seed);
 vector<Pt>P; for(int x=0;x<N;x++)for(int y=0;y<N;y++)if(((x+y)&1)==par)P.push_back({x,y}); int n=P.size();
 map<Key, vector<int>> mp;
 for(int i=0;i<n;i++)for(int j=i+1;j<n;j++){Key k=lineKey(P[i],P[j]); if(!mp.count(k)){vector<int> v; for(int t=0;t<n;t++) if(k.A*P[t].x+k.B*P[t].y+k.C==0) v.push_back(t); if(v.size()>=3) mp[k]=v;}}
 vector<vector<int>> lines; for(auto &kv:mp) lines.push_back(kv.second);
 sort(lines.begin(),lines.end(),[](auto&a,auto&b){ if(a.size()!=b.size())return a.size()>b.size(); return a<b;});
 lines.erase(unique(lines.begin(),lines.end()),lines.end());
 int m=lines.size(); vector<vector<int>> pl(n); for(int li=0;li<m;li++)for(int p:lines[li])pl[p].push_back(li);
 cerr<<"points "<<n<<" lines "<<m<<" K "<<K<<" seed "<<seed<<"\n";
 auto costCounts=[&](vector<short>&cnt){int c=0;for(short v:cnt)if(v>2)c+=v-2;return c;};
 auto drem=[&](int p, vector<short>&cnt){int d=0;for(int li:pl[p]) if(cnt[li]>2) d--; return d;};
 auto dadd=[&](int p, vector<short>&cnt){int d=0;for(int li:pl[p]) if(cnt[li]>=2) d++; return d;};
 auto verify=[&](vector<int>&sel){ vector<Pt> S; for(int i:sel)S.push_back(P[i]); for(int i=0;i<(int)S.size();i++)for(int j=i+1;j<(int)S.size();j++){Key k=lineKey(S[i],S[j]);int c=0; for(auto&p:S) if(k.A*p.x+k.B*p.y+k.C==0) if(++c>=3)return false;} return true;};
 auto printSol=[&](vector<int>&sel){ vector<pair<int,int>> out; for(int i:sel)out.push_back({P[i].x,P[i].y}); sort(out.begin(),out.end()); cout<<"["; for(size_t i=0;i<out.size();i++){ if(i)cout<<","; cout<<"["<<out[i].first<<","<<out[i].second<<"]";} cout<<"]\n"; };
 int best=1e9; vector<int> bestsel; long long moves=0, starts=0;
 auto end=chrono::steady_clock::now()+chrono::seconds(TL);
 uniform_real_distribution<double> U(0,1);
 while(chrono::steady_clock::now()<end){
   starts++;
   vector<int> sel; vector<char> in(n,false); vector<short> cnt(m,0);
   vector<int> cand(n); iota(cand.begin(),cand.end(),0); shuffle(cand.begin(),cand.end(),rng);
   for(int step=0;step<K;step++){
     int bestc=1e9; vector<int> opts;
     bool full = step>K-6 || U(rng)<0.35;
     int samples = full ? cand.size() : min((int)cand.size(), 120);
     for(int ss=0;ss<samples;ss++){
       int idx = full? ss : uniform_int_distribution<int>(0,cand.size()-1)(rng);
       int p=cand[idx]; int add=dadd(p,cnt);
       if(add<bestc){bestc=add;opts.clear();opts.push_back(p);} else if(add==bestc) opts.push_back(p);
     }
     int p=opts[uniform_int_distribution<int>(0,opts.size()-1)(rng)];
     sel.push_back(p); in[p]=true; for(int li:pl[p])cnt[li]++;
     cand.erase(find(cand.begin(),cand.end(),p));
   }
   int cost=costCounts(cnt); double T=1.5;
   for(int it=0;it<2000000 && chrono::steady_clock::now()<end;it++){
     if(cost==0){ if(verify(sel)){ cerr<<"FOUND starts "<<starts<<" moves "<<moves<<"\n"; printSol(sel); return 0; }}
     vector<int> badlines; badlines.reserve(32);
     for(int li=0;li<m;li++) if(cnt[li]>2) badlines.push_back(li);
     int rem=-1;
     if(!badlines.empty() && U(rng)<0.95){
       int li=badlines[uniform_int_distribution<int>(0,badlines.size()-1)(rng)];
       vector<int> pts; for(int p:lines[li]) if(in[p]) pts.push_back(p);
       rem=pts[uniform_int_distribution<int>(0,pts.size()-1)(rng)];
     } else rem=sel[uniform_int_distribution<int>(0,sel.size()-1)(rng)];
     int oldcost=cost;
     int dr=drem(rem,cnt); for(int li:pl[rem])cnt[li]--; in[rem]=false; auto itrem=find(sel.begin(),sel.end(),rem); *itrem=sel.back(); sel.pop_back(); int after=cost+dr;
     int bestd=1e9; vector<int> opts;
     bool full=(cost<=3 && U(rng)<0.45) || U(rng)<0.05;
     int samples=full?n:140;
     for(int ss=0;ss<samples;ss++){
       int q = full? ss : uniform_int_distribution<int>(0,n-1)(rng);
       if(in[q]) continue;
       int da=dadd(q,cnt);
       if(da<bestd){bestd=da;opts.clear();opts.push_back(q);} else if(da==bestd) opts.push_back(q);
     }
     int q;
     if(opts.empty()) q=rem;
     else if(bestd>0 && U(rng)<0.03){ do{q=uniform_int_distribution<int>(0,n-1)(rng);}while(in[q]); bestd=dadd(q,cnt); }
     else q=opts[uniform_int_distribution<int>(0,opts.size()-1)(rng)];
     int newcost=after+bestd;
     bool accept = newcost<=oldcost || U(rng)<exp((oldcost-newcost)/max(0.05,T));
     if(!accept){ q=rem; newcost=after+dadd(q,cnt); }
     sel.push_back(q); in[q]=true; for(int li:pl[q])cnt[li]++; cost=newcost; moves++;
     if(cost<best){best=cost; bestsel=sel; cerr<<"best "<<best<<" starts "<<starts<<" moves "<<moves<<"\n"; printSol(bestsel); cerr.flush();}
     T*=0.99998;
     if(T<0.05) T=0.05;
   }
 }
 cerr<<"NOT_FOUND best "<<best<<" starts "<<starts<<" moves "<<moves<<"\n"; printSol(bestsel);
 return 1;
}
