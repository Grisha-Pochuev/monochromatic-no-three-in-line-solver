#include <bits/stdc++.h>
using namespace std;

struct Pt { int x, y; };
struct Option { vector<int> pts; };

int n = 18;
int parity = 0;
int target = 28;
double deadlineSec = 300.0;
int shardId = 0;
int shardCount = 1;

vector<Pt> pts;
vector<vector<int>> lines;
vector<vector<int>> pointLines;
vector<vector<Option>> rowOptions;
vector<int> orderRows;
vector<unsigned char> cnt;
vector<int> selected;
long long nodes = 0;
int best = 0;
auto startTime = chrono::steady_clock::now();

array<int, 3> canonical(Pt a, Pt b) {
    int A = b.y - a.y;
    int B = a.x - b.x;
    int C = -(A * a.x + B * a.y);
    int g = std::gcd(std::gcd(abs(A), abs(B)), abs(C));
    A /= g; B /= g; C /= g;
    if (A < 0 || (A == 0 && B < 0)) { A = -A; B = -B; C = -C; }
    return {A, B, C};
}

bool onLine(array<int, 3> L, Pt q) {
    return L[0] * q.x + L[1] * q.y + L[2] == 0;
}

void build() {
    for (int y = 0; y < n; y++) {
        for (int x = 0; x < n; x++) {
            if (((x + y) & 1) == parity) pts.push_back({x, y});
        }
    }

    map<array<int, 3>, vector<int>> rawLines;
    for (int i = 0; i < (int)pts.size(); i++) {
        for (int j = i + 1; j < (int)pts.size(); j++) {
            auto key = canonical(pts[i], pts[j]);
            if (!rawLines.count(key)) {
                vector<int> line;
                for (int r = 0; r < (int)pts.size(); r++) {
                    if (onLine(key, pts[r])) line.push_back(r);
                }
                if (line.size() >= 3) rawLines[key] = line;
            }
        }
    }

    set<vector<int>> seen;
    for (auto &kv : rawLines) {
        auto line = kv.second;
        sort(line.begin(), line.end());
        if (seen.insert(line).second) lines.push_back(line);
    }

    pointLines.assign(pts.size(), {});
    for (int li = 0; li < (int)lines.size(); li++) {
        for (int pi : lines[li]) pointLines[pi].push_back(li);
    }

    cnt.assign(lines.size(), 0);
    orderRows = {8,9,7,10,6,11,5,12,4,13,3,14,2,15,1,16,0,17};
    rowOptions.resize(n);

    for (int y = 0; y < n; y++) {
        vector<int> cells;
        for (int i = 0; i < (int)pts.size(); i++) {
            if (pts[i].y == y) cells.push_back(i);
        }
        rowOptions[y].push_back({{}});
        for (int a : cells) rowOptions[y].push_back({{a}});
        for (int i = 0; i < (int)cells.size(); i++) {
            for (int j = i + 1; j < (int)cells.size(); j++) {
                rowOptions[y].push_back({{cells[i], cells[j]}});
            }
        }
        sort(rowOptions[y].begin(), rowOptions[y].end(), [](const Option &a, const Option &b) {
            if (a.pts.size() != b.pts.size()) return a.pts.size() > b.pts.size();
            return a.pts < b.pts;
        });
    }

    cerr << "pts " << pts.size() << " lines " << lines.size()
         << " target " << target << " shard " << shardId << "/" << shardCount << "\n";
}

inline bool canAdd(int pi) {
    for (int li : pointLines[pi]) if (cnt[li] >= 2) return false;
    return true;
}

inline void addPoint(int pi) {
    selected.push_back(pi);
    for (int li : pointLines[pi]) cnt[li]++;
}

inline void removeLastPoint(int pi) {
    for (int li : pointLines[pi]) cnt[li]--;
    selected.pop_back();
}

int colUpper(int rpos) {
    bool remRow[18] = {false};
    for (int k = rpos; k < n; k++) remRow[orderRows[k]] = true;

    int sum = 0;
    for (int x = 0; x < n; x++) {
        int used = 0;
        int avail = 0;
        for (int pi = 0; pi < (int)pts.size(); pi++) {
            if (pts[pi].x != x) continue;
            if (find(selected.begin(), selected.end(), pi) != selected.end()) used++;
            if (remRow[pts[pi].y]) avail++;
        }
        sum += min(2 - used, avail);
    }
    return sum;
}

bool dfs(int rpos, int chosen) {
    nodes++;
    if ((nodes & ((1 << 15) - 1)) == 0) {
        double elapsed = chrono::duration<double>(chrono::steady_clock::now() - startTime).count();
        cerr << "nodes " << nodes << " rpos " << rpos << " chosen " << chosen
             << " best " << best << " time " << elapsed << "\n";
        if (elapsed > deadlineSec) throw runtime_error("timeout");
    }

    if (chosen > best) {
        best = chosen;
        double elapsed = chrono::duration<double>(chrono::steady_clock::now() - startTime).count();
        cerr << "best " << best << " rpos " << rpos << " time " << elapsed << "\n";
    }

    int remRows = n - rpos;
    if (chosen + 2 * remRows < target) return false;
    if (chosen + colUpper(rpos) < target) return false;

    if (rpos == n) {
        if (chosen >= target) {
            cerr << "FOUND\n";
            cout << "[";
            for (int i = 0; i < (int)selected.size(); i++) {
                int pi = selected[i];
                if (i) cout << ",";
                cout << "[" << pts[pi].x << "," << pts[pi].y << "]";
            }
            cout << "]\n";
            return true;
        }
        return false;
    }

    int y = orderRows[rpos];
    for (int oi = 0; oi < (int)rowOptions[y].size(); oi++) {
        if (rpos == 0 && shardCount > 1 && (oi % shardCount) != shardId) continue;

        auto &op = rowOptions[y][oi];
        int s = (int)op.pts.size();
        if (chosen + s > target) continue;
        if (chosen + s + 2 * (remRows - 1) < target) continue;

        bool ok = true;
        for (int pi : op.pts) {
            if (!canAdd(pi)) { ok = false; break; }
        }
        if (!ok) continue;

        for (int pi : op.pts) addPoint(pi);
        if (dfs(rpos + 1, chosen + s)) return true;
        for (int k = (int)op.pts.size() - 1; k >= 0; k--) removeLastPoint(op.pts[k]);
    }
    return false;
}

int main(int argc, char **argv) {
    if (argc > 1) deadlineSec = atof(argv[1]);
    if (argc > 2) shardId = atoi(argv[2]);
    if (argc > 3) shardCount = atoi(argv[3]);
    if (shardId < 0 || shardCount < 1 || shardId >= shardCount) {
        cerr << "Bad shard arguments. Usage: ./dfs18 seconds shard_id shard_count\n";
        return 2;
    }

    build();
    startTime = chrono::steady_clock::now();
    try {
        bool ans = dfs(0, 0);
        double elapsed = chrono::duration<double>(chrono::steady_clock::now() - startTime).count();
        cerr << "DONE ans " << ans << " nodes " << nodes << " best " << best
             << " time " << elapsed << " shard " << shardId << "/" << shardCount << "\n";
        return ans ? 0 : 1;
    } catch (exception &e) {
        cerr << "TIMEOUT nodes " << nodes << " best " << best
             << " shard " << shardId << "/" << shardCount << "\n";
        return 124;
    }
}
