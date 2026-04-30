\ Small MIPLIB-style LP relaxation sample for framework smoke tests.
Minimize
 obj: 0.8 x1 + 1.4 x2 + 0.6 x3 + 1.1 x4
Subject To
 c1: x1 + x2 + x4 >= 1
 c2: x2 + x3 >= 1
 c3: x1 + x3 + x4 <= 2.2
Bounds
 0 <= x1 <= 1
 0 <= x2 <= 1
 0 <= x3 <= 1
 0 <= x4 <= 1
End
