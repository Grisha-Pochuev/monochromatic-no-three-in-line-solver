// Exhaustively test whether the recorded 34-point near-solution can be repaired
// by removing exactly K of its points and adding exactly K outside points.
//
// Build and run, for example:
//   g++ -O3 -std=c++17 verify_near_34_neighborhood.cpp -o verify_near_34_neighborhood
//   for k in {1..9}; do ./verify_near_34_neighborhood "$k"; done
//
// Exit 0 means the complete K-swap neighbourhood contains no valid 34-point
// configuration. Exit 1 means that a valid repair was found and printed.

#include <bits/stdc++.h>
using namespace std;

struct Pt { int x, y; };
struct Key {
    int A, B, C;
    bool operator<(Key const& other) const {
        return tie(A, B, C) < tie(other.A, other.B, other.C);
    }
};

int gcd3(int a, int b, int c) {
    return gcd(gcd(abs(a), abs(b)), abs(c));
}

Key line_key(Pt p, Pt q) {
    int A = q.y - p.y;
    int B = p.x - q.x;
    int C = -(A * p.x + B * p.y);
    int g = gcd3(A, B, C);
    A /= g; B /= g; C /= g;
    if (A < 0 || (A == 0 && B < 0)) {
        A = -A; B = -B; C = -C;
    }
    return {A, B, C};
}

int main(int argc, char** argv) {
    const int K = argc > 1 ? atoi(argv[1]) : 9;
    if (K < 1 || K > 17) {
        cerr << "K must lie in 1..17\n";
        return 2;
    }

    vector<Pt> points;
    for (int x = 0; x < 22; ++x)
        for (int y = 0; y < 22; ++y)
            if (((x + y) & 1) == 0)
                points.push_back({x, y});
    const int n = points.size();

    map<pair<int, int>, int> point_index;
    for (int i = 0; i < n; ++i)
        point_index[{points[i].x, points[i].y}] = i;

    const vector<pair<int, int>> raw = {
        {0,6},{0,10},{1,15},{1,17},{2,14},{2,18},{3,1},{3,7},
        {4,14},{4,16},{5,1},{5,3},{6,20},{8,0},{8,4},{11,15},
        {11,19},{12,0},{12,2},{13,21},{14,0},{14,16},{15,21},
        {16,8},{17,5},{17,11},{18,18},{18,20},{19,13},{19,19},
        {20,2},{20,4},{21,7},{21,11}
    };

    vector<int> original;
    vector<char> in_original(n, false);
    for (auto [x, y] : raw) {
        int index = point_index[{x, y}];
        original.push_back(index);
        in_original[index] = true;
    }

    map<Key, vector<int>> line_map;
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            Key key = line_key(points[i], points[j]);
            if (line_map.count(key)) continue;
            vector<int> members;
            for (int t = 0; t < n; ++t) {
                if (key.A * points[t].x + key.B * points[t].y + key.C == 0)
                    members.push_back(t);
            }
            if (members.size() >= 3)
                line_map[key] = move(members);
        }
    }

    vector<vector<int>> lines;
    for (auto& entry : line_map)
        lines.push_back(entry.second);
    const int line_count = lines.size();

    vector<vector<int>> point_lines(n);
    for (int line = 0; line < line_count; ++line)
        for (int point : lines[line])
            point_lines[point].push_back(line);

    vector<int> counts(line_count, 0);
    for (int point : original)
        for (int line : point_lines[point])
            ++counts[line];

    vector<int> outside;
    for (int i = 0; i < n; ++i)
        if (!in_original[i])
            outside.push_back(i);
    vector<int> outside_id(n, -1);
    for (int i = 0; i < static_cast<int>(outside.size()); ++i)
        outside_id[outside[i]] = i;

    vector<vector<int>> outside_on_line(line_count);
    for (int line = 0; line < line_count; ++line)
        for (int point : lines[line])
            if (!in_original[point])
                outside_on_line[line].push_back(point);

    vector<int> blocker_count(n, 0);
    for (int point : outside)
        for (int line : point_lines[point])
            if (counts[line] >= 2)
                ++blocker_count[point];

    array<unsigned long long, 4> safe_mask{};
    for (int point : outside) {
        if (blocker_count[point] == 0) {
            int id = outside_id[point];
            safe_mask[id / 64] |= 1ULL << (id % 64);
        }
    }

    vector<int> removed, added;
    long long removal_leaves = 0;
    long long pruned_leaves = 0;
    auto started = chrono::steady_clock::now();

    function<bool(int, int, vector<int>&)> add_search =
        [&](int position, int needed, vector<int>& candidates) -> bool {
            if (needed == 0) return true;
            if (static_cast<int>(candidates.size()) - position < needed)
                return false;

            for (int i = position;
                 i <= static_cast<int>(candidates.size()) - needed;
                 ++i) {
                int point = candidates[i];
                bool allowed = true;
                for (int line : point_lines[point]) {
                    if (counts[line] >= 2) {
                        allowed = false;
                        break;
                    }
                }
                if (!allowed) continue;

                for (int line : point_lines[point]) ++counts[line];
                added.push_back(point);
                if (add_search(i + 1, needed - 1, candidates)) return true;
                added.pop_back();
                for (int line : point_lines[point]) --counts[line];
            }
            return false;
        };

    function<bool(int, int)> remove_search =
        [&](int position, int needed) -> bool {
            if (needed == 0) {
                ++removal_leaves;
                for (int count : counts) {
                    if (count > 2) {
                        ++pruned_leaves;
                        return false;
                    }
                }

                int safe_count = 0;
                for (auto word : safe_mask)
                    safe_count += __builtin_popcountll(word);
                if (safe_count < K) {
                    ++pruned_leaves;
                    return false;
                }

                vector<int> candidates;
                candidates.reserve(safe_count);
                for (int id = 0; id < static_cast<int>(outside.size()); ++id) {
                    if ((safe_mask[id / 64] >> (id % 64)) & 1ULL)
                        candidates.push_back(outside[id]);
                }
                return add_search(0, K, candidates);
            }

            if (static_cast<int>(original.size()) - position < needed)
                return false;

            for (int i = position;
                 i <= static_cast<int>(original.size()) - needed;
                 ++i) {
                int point = original[i];
                for (int line : point_lines[point]) {
                    int before = counts[line];
                    --counts[line];
                    if (before == 2) {
                        for (int candidate : outside_on_line[line]) {
                            --blocker_count[candidate];
                            if (blocker_count[candidate] == 0) {
                                int id = outside_id[candidate];
                                safe_mask[id / 64] |= 1ULL << (id % 64);
                            }
                        }
                    }
                }

                removed.push_back(point);
                if (remove_search(i + 1, needed - 1)) return true;
                removed.pop_back();

                for (int line : point_lines[point]) {
                    int before = counts[line];
                    if (before == 1) {
                        for (int candidate : outside_on_line[line]) {
                            if (blocker_count[candidate] == 0) {
                                int id = outside_id[candidate];
                                safe_mask[id / 64] &= ~(1ULL << (id % 64));
                            }
                            ++blocker_count[candidate];
                        }
                    }
                    ++counts[line];
                }
            }
            return false;
        };

    bool found = remove_search(0, K);
    double seconds = chrono::duration<double>(
        chrono::steady_clock::now() - started
    ).count();

    cout << "K=" << K
         << " found_repair=" << (found ? "yes" : "no")
         << " removal_leaves=" << removal_leaves
         << " pruned_leaves=" << pruned_leaves
         << " seconds=" << fixed << setprecision(3) << seconds << "\n";

    if (!found) return 0;

    vector<char> selected(n, false);
    for (int point : original) selected[point] = true;
    for (int point : removed) selected[point] = false;
    for (int point : added) selected[point] = true;

    vector<pair<int, int>> answer;
    for (int i = 0; i < n; ++i)
        if (selected[i])
            answer.push_back({points[i].x, points[i].y});
    sort(answer.begin(), answer.end());

    cerr << "A valid repair was found; the neighbourhood exclusion is false.\n";
    for (auto [x, y] : answer)
        cerr << "(" << x << "," << y << ") ";
    cerr << "\n";
    return 1;
}
