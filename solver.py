from mip import Model, minimize, BINARY, xsum, OptimizationStatus
import sys

# path = "../graduate-second/second/testcase/4_3_30_15_30/testcase"
path = "../graduate-second/second/testcase/3_3_20_10_30_x100/testcase"
# path = "../graduate-second/second/testcase/5_3_40_15_30/testcase"
# path = "../second/testcase/3_3_20_7_0/testcase"
# path = "test"

result_path = "results"
result_file = open(result_path, 'w')
datalist = []

for test_number in range(20):
    print("solve {}\n".format(test_number))

    # manage input
    f = open(path + str(test_number), 'r')
    data = f.read()
    f.close()
    stream = data.split()

    # constant
    stack_size = int(stream[0])
    tier_size = int(stream[1])
    horizon = int(stream[2])
    blocks = int(stream[3])
    filling_rate = int(stream[4])
    initially_located = int(stream[5])

    # blocks
    tmp_blocks = []
    arrivings = []
    expecteds = []
    for i in range(initially_located):
        tmp_blocks.append((int(stream[6 + i]), 0, i))
    for i in range(blocks - initially_located):
        tmp_blocks.append(
            (int(stream[6 + initially_located + 2 * i + 1]), int(stream[6 + initially_located + 2 * i]), i + initially_located))
    print(tmp_blocks)
    tmp_blocks.sort()
    for i in range(blocks):
        arrivings.append(tmp_blocks[i][1])
        expecteds.append(tmp_blocks[i][0])
    print(tmp_blocks)
    print(arrivings)
    print(expecteds)

    # model
    solver = Model("DBRP")

    # variables
    # block n is placed in slot (i, j) in a(n)
    a = [[[[solver.add_var('a({},{},{},{})'.format(i, j, n, t), var_type=BINARY) for t in range(
        horizon + 1)] for n in range(blocks)] for j in range(tier_size)] for i in range(stack_size)]
    # block n is placed in (i, j) in t
    b = [[[[solver.add_var('b({},{},{},{})'.format(i, j, n, t), var_type=BINARY) for t in range(
        horizon + 1)] for n in range(blocks)] for j in range(tier_size)] for i in range(stack_size)]
    # block n is relocated from (i, j) to (k, l) in t
    x = [[[[[[solver.add_var('x({},{},{},{},{},{})'.format(i, j, k, l, n, t), var_type=BINARY) for t in range(horizon + 1)] for n in range(
        blocks)] for l in range(tier_size)] for k in range(stack_size)] for j in range(tier_size)] for i in range(stack_size)]
    # block n in (i, j) is retrieved in t
    y = [[[[solver.add_var('y({},{},{},{})'.format(i, j, n, t), var_type=BINARY) for t in range(
        horizon + 1)] for n in range(blocks)] for j in range(tier_size)] for i in range(stack_size)]
    # block n is retrieved before t
    v = [[solver.add_var('v({},{})'.format(n, t), var_type=BINARY)
          for t in range(horizon + 1)] for n in range(blocks)]
    # variables' constraint
    # for a
    for n in range(blocks):
        for i in range(stack_size):
            for j in range(tier_size):
                for t in range(horizon + 1):
                    if t != arrivings[n]:
                        solver.add_constr(a[i][j][n][t] == 0)
    # for b
    for n in range(blocks):
        for i in range(stack_size):
            for j in range(tier_size):
                for t in range(arrivings[n] + 1):
                    solver.add_constr(b[i][j][n][t] == 0)
    # for x
    for n in range(blocks):
        for i in range(stack_size):
            for j in range(tier_size):
                for k in range(stack_size):
                    for l in range(tier_size):
                        for t in range(horizon + 1):
                            if (i == k) or (t <= arrivings[n]):
                                solver.add_constr(x[i][j][k][l][n][t] == 0)
    # for y
    for n in range(blocks):
        for i in range(stack_size):
            for j in range(tier_size):
                for t in range(expecteds[n]):
                    solver.add_constr(y[i][j][n][t] == 0)
    # for v
    for n in range(blocks):
        for t in range(expecteds[n] + 1):
            solver.add_constr(v[n][t] == 0)

    # objective function
    solver.objective = minimize(xsum(x[i][j][k][l][n][t] for i in range(stack_size) for j in range(
        tier_size) for k in range(stack_size) for l in range(tier_size) for n in range(blocks) for t in range(horizon+1)))

    # constraint

    # 0. initial conditions
    for n in range(blocks):
        initial_number = tmp_blocks[n][2]
        if initial_number < initially_located:
            solver.add_constr(a[initial_number % stack_size][int(initial_number / stack_size)]
                              [n][0] == 1, 'cnst01({})'.format(n))
            print("a[{}][{}][{}][0] == 1".format(initial_number %
                  stack_size, int(initial_number / stack_size), n))

    # 1. Slot (i, j) can hold at most one block in period t
    for i in range(stack_size):
        for j in range(tier_size):
            for t in range(horizon+1):
                solver.add_constr(
                    xsum(a[i][j][n][t] + b[i][j][n][t] for n in range(blocks)) <= 1, 'cnst1({},{},{})'.format(i, j, t))

    # 2. Block n is either on the ground or on another block
    for i in range(stack_size):
        for j in range(1, tier_size):
            for t in range(1, horizon+1):
                solver.add_constr(xsum(
                    a[i][j][n][t] + b[i][j][n][t] - b[i][j - 1][n][t] for n in range(blocks)) <= 0, 'cnst2({},{},{})'.format(i, j, t))

    # 3. At most one movement is possible in period t
    for t in range(1, horizon+1):
        solver.add_constr((xsum(x[i][j][k][l][n][t] for i in range(stack_size) for j in range(
            tier_size) for k in range(stack_size) for l in range(tier_size) for n in range(blocks)) + xsum(a[i][j][n][t] + y[i][j][n][t] for i in range(stack_size) for j in range(tier_size) for n in range(blocks))) <= 1, 'cnst3({})'.format(t))

    # 4. Block n is placed in some slot in its arrival period a(n)
    for n in range(blocks):
        solver.add_constr(xsum(a[i][j][n][arrivings[n]]
                          for i in range(stack_size) for j in range(tier_size)) == 1, 'cnst4({})'.format(n))

    # 5. Block (n + 1) cannot be retrieved before block n
    for n in range(blocks-1):
        solver.add_constr(xsum(v[n][t] for t in range(
            horizon+1)) >= xsum(v[n + 1][t] for t in range(horizon+1)) + 1, 'cnst5({})'.format(n))

    # 6. Block n is not in the bay in period t (> e(n)) iff it is retrieved before t
    for n in range(blocks):
        for t in range(horizon+1):
            solver.add_constr(v[n][t] == xsum(y[i][j][n][s] for i in range(
                stack_size) for j in range(tier_size) for s in range(t)), 'cnst6({},{})'.format(n, t))

    # 7. All the blocks must be retrieved in the planning horizon
    solver.add_constr(xsum(y[i][j][n][t] for i in range(stack_size) for j in range(
        tier_size) for n in range(blocks) for t in range(horizon+1)) == blocks, 'cnst7')

    # 8. Block n can take only three states in period t: not yet arrived, placed, have been retrieved
    for n in range(blocks):
        for t in range(arrivings[n] + 1, horizon+1):
            solver.add_constr(xsum(b[i][j][n][t]  # + v[n][t]
                              for i in range(stack_size) for j in range(tier_size)) + v[n][t] == 1, 'cnst8({},{})'.format(n, t))

    # 9. The state of slot (i, j) in period t is determined
    for i in range(stack_size):
        for j in range(tier_size):
            for n in range(blocks):
                for t in range(arrivings[n] + 1, horizon+1):
                    solver.add_constr(b[i][j][n][t] == b[i][j][n][t - 1] + xsum(x[k][l][i][j][n][t - 1] - x[i][j][k][l][n][t - 1] for k in
                                      range(stack_size) for l in range(tier_size)) - y[i][j][n][t - 1] + a[i][j][n][t - 1], 'cnst9({},{},{},{})'.format(i, j, n, t))

    # 10. The target must be retrieved if on the top
    for i in range(stack_size):
        for j in range(tier_size):
            for n in range(blocks):
                for t in range(expecteds[n], horizon+1):
                    if (j != tier_size - 1):
                        solver.add_constr(b[i][j][n][t] + xsum(v[block][t]
                                          for block in range(n)) - n <= y[i][j][n][t] + xsum(b[i][j][block][t] for block in range(blocks)) + xsum(a[stack][tier][block][t] for stack in range(stack_size) for tier in range(tier_size) for block in range(blocks)))
                    else:
                        solver.add_constr(b[i][j][n][t] + xsum(v[block][t]
                                          for block in range(n)) - n <= y[i][j][n][t] + xsum(a[stack][tier][block][t] for stack in range(stack_size) for tier in range(tier_size) for block in range(blocks)))

    status = solver.optimize(max_seconds=18000)

    print("\n{}\n".format(solver.status))
    if solver.status == OptimizationStatus.OPTIMAL:
        ans = 0
        for i in range(stack_size):
            for j in range(tier_size):
                for k in range(stack_size):
                    if k == i:
                        continue
                    for l in range(tier_size):
                        for n in range(blocks):
                            for t in range(horizon + 1):
                                if x[i][j][k][l][n][t].x >= 0.99:
                                    ans += 1
        print("ans: {}\n".format(ans))
        datalist.append("{}\n".format(ans))
    elif solver.status == OptimizationStatus.INFEASIBLE:
        datalist.append("INFEASIBLE\n")
    else:
        datalist.append("FAIL\n")

    # solver.write('models/model{}.lp'.format(test_number))

    if test_number % 5 == 4:
        datalist.append('\n')

result_file.writelines(datalist)
result_file.close()
