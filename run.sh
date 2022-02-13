#! /bin/tcsh -f

set path = (/sbin /bin /usr/sbin /usr/bin /usr/local/sbin /usr/local/bin $HOME/bin $HOME/.cargo/bin)

# for setting up
mkdir -p results
mkdir -p results/voluntary_immediate
mkdir -p results/voluntary_delay
mkdir -p results/forced_immediate
mkdir -p results/forced_delay
mkdir -p results/dfs

# conditions
set TESTSIZE = 100
set TIME_LIMIT = 1800

# for simulation setting
set TESTS = (\
# "3_3_20_10_10_x100"\
# "3_3_20_10_30_x100"\
# "3_3_30_13_10_x100"\
# "3_3_30_13_30_x100"\
# "3_3_40_15_10_x100"\
# "3_3_40_15_30_x100"\
# \
# "4_3_20_10_10_x100"\
# "4_3_20_10_30_x100"\
# "4_3_30_13_10_x100"\
# "4_3_30_13_30_x100"\
# "4_3_40_15_10_x100"\
# "4_3_40_15_30_x100"\
# \
# "4_4_20_10_10_x100"\
# "4_4_20_10_30_x100"\
# "4_4_30_13_10_x100"\
# "4_4_30_13_30_x100"\
# "4_4_40_15_10_x100"\
# "4_4_40_15_30_x100"\
# \
# "4_4_50_20_10_x100"\
# \
# "5_3_20_10_10_x100"\
# "5_3_20_10_30_x100"\
# "5_3_30_13_10_x100"\
# "5_3_30_13_30_x100"\
# "5_3_40_15_10_x100"\
# "5_3_40_15_30_x100"\
# \
# "6_3_20_10_10_x100"\
# "6_3_20_10_30_x100"\
# "6_3_30_13_10_x100"\
# "6_3_30_13_30_x100"\
# "6_3_40_15_10_x100"\
# "6_3_40_15_30_x100"\
# \
# "6_4_40_15_10_x100"\
# "6_4_40_15_30_x100"\
# reverse
"6_5_70_30_10_x100"\
# reverse
"6_4_50_20_10_x100"\
"6_4_50_20_30_x100"\
"6_4_60_25_10_x100"\
"6_4_60_25_30_x100"\
"6_5_70_30_30_x100"\
)

set i = 1
while ( $i <= $#TESTS )
    # i番目のテストが実行される
    set INSTANCE = $TESTS[$i]

    # 解く種類を指定

    mkdir -p results/forced_immediate/$INSTANCE
    mkdir -p results/forced_delay/$INSTANCE
    # mkdir -p results/voluntary_immediate/$INSTANCE
    # mkdir -p results/voluntary_delay/$INSTANCE

    # cargo build --release

    set TESTCASE = 0
    while ( $TESTCASE < $TESTSIZE )
        # TESTCASE番目のインスタンスが解かれる

        python3 solver.py 1 1 $TESTS[$i] $TESTCASE $TIME_LIMIT
        python3 solver.py 1 2 $TESTS[$i] $TESTCASE $TIME_LIMIT
        # python3 solver.py 2 1 $TESTS[$i] $TESTCASE $TIME_LIMIT
        # python3 solver.py 2 2 $TESTS[$i] $TESTCASE $TIME_LIMIT
        @ TESTCASE = $TESTCASE + 1
    end
    cd graduate-bencher
    cargo run --release ../results/forced_immediate/$INSTANCE $TESTSIZE
    cargo run --release ../results/forced_delay/$INSTANCE $TESTSIZE
    # cargo run --release ../results/voluntary_immediate/$INSTANCE $TESTSIZE
    # cargo run --release ../results/voluntary_delay/$INSTANCE $TESTSIZE
    cd ..
    cd graduate-checker
    cargo run --release ../results/forced_immediate/$INSTANCE $TESTSIZE
    cargo run --release ../results/forced_delay/$INSTANCE $TESTSIZE
    # cargo run --release ../results/voluntary_immediate/$INSTANCE $TESTSIZE
    # cargo run --release ../results/voluntary_delay/$INSTANCE $TESTSIZE
    cd ..
    @ i = $i + 1
end