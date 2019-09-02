# Input: 1->2->4, 1->3->4
# Output: 1->1->2->3->4->4
l1 = [1, 2, 4]
l2 = [1, 3, 4]
l_join = l1 + l2
l_join.sort()
print(l_join)