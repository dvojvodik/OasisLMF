#!/usr/bin/env -S bash -euET -o pipefail -O inherit_errexit
SCRIPT=$(readlink -f "$0") && cd $(dirname "$SCRIPT")

# --- Script Init ---

mkdir -p log
rm -R -f log/*

# --- Setup run dirs ---

find output -type f -not -name '*summary-info*' -not -name '*.json' -exec rm -R -f {} +

rm -R -f /tmp/%FIFO_DIR%/fifo/*
rm -R -f work/*
mkdir work/kat/

mkdir work/gul_S1_summaryleccalc
mkdir work/gul_S1_summaryaalcalc
mkdir work/il_S1_summaryleccalc
mkdir work/il_S1_summaryaalcalc

mkfifo /tmp/%FIFO_DIR%/fifo/gul_P17

mkfifo /tmp/%FIFO_DIR%/fifo/gul_S1_summary_P17
mkfifo /tmp/%FIFO_DIR%/fifo/gul_S1_summary_P17.idx
mkfifo /tmp/%FIFO_DIR%/fifo/gul_S1_eltcalc_P17
mkfifo /tmp/%FIFO_DIR%/fifo/gul_S1_summarycalc_P17
mkfifo /tmp/%FIFO_DIR%/fifo/gul_S1_pltcalc_P17

mkfifo /tmp/%FIFO_DIR%/fifo/il_P17

mkfifo /tmp/%FIFO_DIR%/fifo/il_S1_summary_P17
mkfifo /tmp/%FIFO_DIR%/fifo/il_S1_summary_P17.idx
mkfifo /tmp/%FIFO_DIR%/fifo/il_S1_eltcalc_P17
mkfifo /tmp/%FIFO_DIR%/fifo/il_S1_summarycalc_P17
mkfifo /tmp/%FIFO_DIR%/fifo/il_S1_pltcalc_P17



# --- Do insured loss computes ---
eltcalc -s < /tmp/%FIFO_DIR%/fifo/il_S1_eltcalc_P17 > work/kat/il_S1_eltcalc_P17 & pid1=$!
summarycalctocsv -s < /tmp/%FIFO_DIR%/fifo/il_S1_summarycalc_P17 > work/kat/il_S1_summarycalc_P17 & pid2=$!
pltcalc -s < /tmp/%FIFO_DIR%/fifo/il_S1_pltcalc_P17 > work/kat/il_S1_pltcalc_P17 & pid3=$!
tee < /tmp/%FIFO_DIR%/fifo/il_S1_summary_P17 /tmp/%FIFO_DIR%/fifo/il_S1_eltcalc_P17 /tmp/%FIFO_DIR%/fifo/il_S1_summarycalc_P17 /tmp/%FIFO_DIR%/fifo/il_S1_pltcalc_P17 work/il_S1_summaryaalcalc/P17.bin work/il_S1_summaryleccalc/P17.bin > /dev/null & pid4=$!
tee < /tmp/%FIFO_DIR%/fifo/il_S1_summary_P17.idx work/il_S1_summaryleccalc/P17.idx > /dev/null & pid5=$!
summarycalc -m -f  -1 /tmp/%FIFO_DIR%/fifo/il_S1_summary_P17 < /tmp/%FIFO_DIR%/fifo/il_P17 &

# --- Do ground up loss computes ---
eltcalc -s < /tmp/%FIFO_DIR%/fifo/gul_S1_eltcalc_P17 > work/kat/gul_S1_eltcalc_P17 & pid6=$!
summarycalctocsv -s < /tmp/%FIFO_DIR%/fifo/gul_S1_summarycalc_P17 > work/kat/gul_S1_summarycalc_P17 & pid7=$!
pltcalc -s < /tmp/%FIFO_DIR%/fifo/gul_S1_pltcalc_P17 > work/kat/gul_S1_pltcalc_P17 & pid8=$!
tee < /tmp/%FIFO_DIR%/fifo/gul_S1_summary_P17 /tmp/%FIFO_DIR%/fifo/gul_S1_eltcalc_P17 /tmp/%FIFO_DIR%/fifo/gul_S1_summarycalc_P17 /tmp/%FIFO_DIR%/fifo/gul_S1_pltcalc_P17 work/gul_S1_summaryaalcalc/P17.bin work/gul_S1_summaryleccalc/P17.bin > /dev/null & pid9=$!
tee < /tmp/%FIFO_DIR%/fifo/gul_S1_summary_P17.idx work/gul_S1_summaryleccalc/P17.idx > /dev/null & pid10=$!
summarycalc -m -i  -1 /tmp/%FIFO_DIR%/fifo/gul_S1_summary_P17 < /tmp/%FIFO_DIR%/fifo/gul_P17 &

eve 17 20 | getmodel | gulcalc -S100 -L100 -r -a1 -i - | tee /tmp/%FIFO_DIR%/fifo/gul_P17 | fmcalc -a2 > /tmp/%FIFO_DIR%/fifo/il_P17  &

wait $pid1 $pid2 $pid3 $pid4 $pid5 $pid6 $pid7 $pid8 $pid9 $pid10


# --- Do insured loss kats ---

kat -s work/kat/il_S1_eltcalc_P17 > output/il_S1_eltcalc.csv & kpid1=$!
kat work/kat/il_S1_pltcalc_P17 > output/il_S1_pltcalc.csv & kpid2=$!
kat work/kat/il_S1_summarycalc_P17 > output/il_S1_summarycalc.csv & kpid3=$!

# --- Do ground up loss kats ---

kat -s work/kat/gul_S1_eltcalc_P17 > output/gul_S1_eltcalc.csv & kpid4=$!
kat work/kat/gul_S1_pltcalc_P17 > output/gul_S1_pltcalc.csv & kpid5=$!
kat work/kat/gul_S1_summarycalc_P17 > output/gul_S1_summarycalc.csv & kpid6=$!
wait $kpid1 $kpid2 $kpid3 $kpid4 $kpid5 $kpid6
