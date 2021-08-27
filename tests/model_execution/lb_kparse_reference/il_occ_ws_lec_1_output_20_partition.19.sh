#!/usr/bin/env -S bash -euET -o pipefail -O inherit_errexit
SCRIPT=$(readlink -f "$0") && cd $(dirname "$SCRIPT")

# --- Script Init ---

mkdir -p log
rm -R -f log/*

# --- Setup run dirs ---

find output -type f -not -name '*summary-info*' -not -name '*.json' -exec rm -R -f {} +

rm -R -f fifo/*
rm -R -f work/*
mkdir work/kat/

fmpy -a2 --create-financial-structure-files
mkdir work/il_S1_summaryleccalc

mkfifo fifo/il_P20

mkfifo fifo/il_S1_summary_P20
mkfifo fifo/il_S1_summary_P20.idx



# --- Do insured loss computes ---
tee < fifo/il_S1_summary_P20 work/il_S1_summaryleccalc/P20.bin > /dev/null & pid1=$!
tee < fifo/il_S1_summary_P20.idx work/il_S1_summaryleccalc/P20.idx > /dev/null & pid2=$!
summarycalc -m -f  -1 fifo/il_S1_summary_P20 < fifo/il_P20 &

eve 20 20 | getmodel | gulcalc -S100 -L100 -r -a0 -i - | fmpy -a2 > fifo/il_P20  &

wait $pid1 $pid2


# --- Do insured loss kats ---
