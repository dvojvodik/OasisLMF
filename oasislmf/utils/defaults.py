__all__ = [
    'COVERAGE_TYPES',
    'DEDUCTIBLE_AND_LIMIT_TYPES',
    'DEDUCTIBLE_CODES',
    'FM_LEVELS',
    'FM_TERMS',
    'get_calc_rules',
    'get_default_accounts_profile',
    'get_default_deterministic_analysis_settings',
    'get_default_exposure_profile',
    'get_default_fm_aggregation_profile',
    'get_default_unified_profile',
    'KTOOLS_ALLOC_RULE',
    'KTOOLS_FIFO_RELATIVE',
    'KTOOLS_DEBUG',
    'KTOOLS_MEM_LIMIT',
    'KTOOLS_NUM_PROCESSES',
    'LIMIT_CODES',
    'OASIS_FILES_PREFIXES',
    'OASIS_KEYS_STATUS',
    'OASIS_TASK_STATUS',
    'PERILS',
    'PERIL_GROUPS',
    'STATIC_DATA_FP',
    'update_calc_rules'
]

import os

from collections import OrderedDict

from .data import (
    fast_zip_arrays,
    get_dataframe,
    get_json,
)


COVT_BLD = 1
COVT_OTH = 2
COVT_CON = 3
COVT_BIT = 4
COVT_PDM = 5
COVT_ALL = 6

COVERAGE_TYPES = OrderedDict({
    'buildings': {'id': COVT_BLD, 'desc': 'buildings'},
    'other': {'id': COVT_OTH, 'desc': 'other (typically appurtenant structures)'},
    'contents': {'id': COVT_CON, 'desc': 'contents'},
    'bi': {'id': COVT_BIT, 'desc': 'business interruption'},
    'pd': {'id': COVT_PDM, 'desc': 'property damage (buildings + other + contents)'},
    'all': {'id': COVT_ALL, 'desc': 'all (property damage + business interruption)'}
})

DED_CODE_REG = 0
DED_CODE_ANAGG = 1
DED_CODE_FRDED = 2
DED_CODE_NRDED = 3
DED_CODE_RSDED = 4
DED_CODE_CEAHO = 5
DED_CODE_CEAHOC = 6

DEDUCTIBLE_CODES = OrderedDict({
    'reg': {'id': DED_CODE_REG, 'desc': 'Regular'},
    'anagg': {'id': DED_CODE_ANAGG, 'desc': 'Annual aggregate'},
    'frded': {'id': DED_CODE_FRDED, 'desc': 'Franchise deductible'},
    'nrded': {'id': DED_CODE_NRDED, 'desc': 'Non-residential deductible'},
    'rsded': {'id': DED_CODE_RSDED, 'desc': 'Residential deductible'},
    'ceaho': {'id': DED_CODE_CEAHO, 'desc': 'CEA Homeowners'},
    'ceahoc': {'id': DED_CODE_CEAHOC, 'desc': 'CEA Homeowners Choice'}
})

DED_LIMIT_TYPE_FLT = 0
DED_LIMIT_TYPE_PCLOSS = 1
DED_LIMIT_TYPE_PCTIV = 2

DEDUCTIBLE_AND_LIMIT_TYPES = OrderedDict({
    'flat': {'id': DED_LIMIT_TYPE_FLT, 'desc': 'Flat monetary amount'},
    'pcloss': {'id': DED_LIMIT_TYPE_PCLOSS, 'desc': 'Percentage of loss'},
    'pctiv': {'id': DED_LIMIT_TYPE_PCTIV, 'desc': 'Percentage of TIV'}
})

FML_SITCOV = 1
FML_SITPDM = 2
FML_SITALL = 3
FML_CNDCOV = 4
FML_CNDPDM = 5
FML_CNDALL = 6
FML_POLCOV = 7
FML_POLPDM = 8
FML_POLALL = 9
FML_POLLAY = 10
FML_ACCCOV = 11
FML_ACCPDM = 12
FML_ACCALL = 13

FM_LEVELS = OrderedDict({
    'site coverage': {'id': FML_SITCOV, 'desc': 'site coverage'},
    'site pd': {'id': FML_SITPDM, 'desc': 'site property damage'},
    'site all': {'id': FML_SITALL, 'desc': 'site all (coverage + property damage)'},
    'cond coverage': {'id': FML_CNDCOV, 'desc': 'conditional coverage'},
    'cond pd': {'id': FML_CNDPDM, 'desc': 'conditional property damage'},
    'cond all': {'id': FML_CNDALL, 'desc': 'conditional all (coverage + property damage)'},
    'policy coverage': {'id': FML_POLCOV, 'desc': 'policy coverage'},
    'policy pd': {'id': FML_POLPDM, 'desc': 'policy property damage'},
    'policy all': {'id': FML_POLALL, 'desc': 'policy all (coverage + property damage)'},
    'policy layer': {'id': FML_POLLAY, 'desc': 'policy layer'},
    'account coverage': {'id': FML_ACCCOV, 'desc': 'account coverage'},
    'account pd': {'id': FML_ACCPDM, 'desc': 'account property damage'},
    'account all': {'id': FML_ACCALL, 'desc': 'account all (coverage + property damage)'}
})

FMT_TIV = 'tiv'
FMT_DED = 'ded'
FMT_DED_MIN = 'ded_min',
FMT_DED_MAX = 'ded_max',
FMT_LIM = 'lim'
FMT_SHR = 'shr'

FM_TERMS = OrderedDict({
    'tiv': {'id': FMT_TIV, 'desc': 'TIV'},
    'deductible': {'id': FMT_DED, 'desc': 'Deductible'},
    'deductible_min': {'id': FMT_DED_MIN, 'desc': 'DeductibleMin'},
    'deductible_max': {'id': FMT_DED_MAX, 'desc': 'DeductibleMax'},
    'limit': {'id': FMT_LIM, 'desc': 'Limit'},
    'share': {'id': FMT_SHR, 'desc': 'Share'}
})

LIM_CODE_REG = 0
LIM_CODE_ANAGG = 1

LIMIT_CODES = OrderedDict({
    'reg': {'id': LIM_CODE_REG, 'desc': 'Regular'},
    'anagg': {'id': LIM_CODE_ANAGG, 'desc': 'Annual aggregate'}
})

OASIS_KEYS_SC = 'success'
OASIS_KEYS_FL = 'fail'
OASIS_KEYS_NM = 'nomatch'

OASIS_KEYS_STATUS = {
    'success': {'id': OASIS_KEYS_SC, 'desc': 'Success'},
    'fail': {'id': OASIS_KEYS_FL, 'desc': 'Failure'},
    'nomatch': {'id': OASIS_KEYS_NM, 'desc': 'No match'}
}

OASIS_TASK_PN = 'PENDING'
OASIS_TASK_RN = 'RUNNING'
OASIS_TASK_SC = 'SUCCESS'
OASIS_TASK_FL = 'FAILURE'

OASIS_TASK_STATUS = {
    'pending': {'id': OASIS_TASK_PN, 'desc': 'Pending'},
    'running': {'id': OASIS_TASK_RN, 'desc': 'Running'},
    'success': {'id': OASIS_TASK_SC, 'desc': 'Success'},
    'failure': {'id': OASIS_TASK_FL, 'desc': 'Failure'}
}

PRL_BBF = 'BBF'
PRL_BFR = 'BFR'
PRL_BSK = 'BSK'
PRL_MNT = 'MNT'
PRL_MTR = 'MTR'
PRL_ORF = 'ORF'
PRL_OSF = 'OSF'
PRL_QEQ = 'QEQ'
PRL_QFF = 'QFF'
PRL_QLF = 'QLF'
PRL_QLS = 'QLS'
PRL_QSL = 'QSL'
PRL_QTS = 'QTS'
PRL_WEC = 'WEC'
PRL_WSS = 'WSS'
PRL_WTC = 'WTC'
PRL_XHL = 'XHL'
PRL_XLT = 'XLT'
PRL_XSL = 'XSL'
PRL_XTD = 'XTD'
PRL_ZFZ = 'ZFZ'
PRL_ZIC = 'ZIC'
PRL_ZSN = 'ZSN'
PRL_ZST = 'ZST'

PRL_GRP_AA1 = 'AA1'
PRL_GRP_BB1 = 'BB1'
PRL_GRP_MM1 = 'MM1'
PRL_GRP_OO1 = 'OO1'
PRL_GRP_QQ1 = 'QQ1'
PRL_GRP_WW1 = 'WW1'
PRL_GRP_WW2 = 'WW2'
PRL_GRP_XX1 = 'XX1'
PRL_GRP_XZ1 = 'XZ1'
PRL_GRP_ZZ1 = 'ZZ1'

PERIL_GROUPS = OrderedDict({
    'all': {'id': PRL_GRP_AA1, 'desc': 'All perils'},
    'wildfire w/ smoke': {'id': PRL_GRP_BB1, 'desc': 'Wildfire with smoke'},
    'terrorism': {'id': PRL_GRP_MM1, 'desc': 'Terrorism'},
    'flood w/o storm surge': {'id': PRL_GRP_OO1, 'desc': 'Flood w/o storm surge'},
    'earthquake': {'id': PRL_GRP_QQ1, 'desc': 'All EQ perils'},
    'windstorm w/ storm surge': {'id': PRL_GRP_WW1, 'desc': 'Windstorm with storm surge'},
    'windstorm w/o storm surge': {'id': PRL_GRP_WW2, 'desc': 'Windstorm w/o storm surge'},
    'convective storm': {'id': PRL_GRP_XX1, 'desc': 'Convective Storm'},
    'convective storm rms': {'id': PRL_GRP_XZ1, 'desc': 'Convective storm (incl winter storm) - for RMS users'},
    'winter storm': {'id': PRL_GRP_ZZ1, 'desc': 'Winter storm'}
})

PERILS = OrderedDict({
    'wildfire': {'id': PRL_BBF, 'desc': 'Wildfire / Bushfire', 'group_peril': PRL_GRP_BB1},
    'noncat': {'id': PRL_BFR, 'desc': 'NonCat', 'group_peril': PRL_GRP_BB1},
    'smoke': {'id': PRL_BSK, 'desc': 'Smoke', 'group_peril': PRL_GRP_BB1},
    'nbcr terrorism': {'id': PRL_MNT, 'desc': 'NBCR Terrorism', 'group_peril': PRL_GRP_MM1},
    'terrorism': {'id': PRL_MTR, 'desc': 'Conventional Terrorism', 'group_peril': PRL_GRP_MM1},
    'river flood': {'id': PRL_ORF, 'desc': 'River / Fluvial Flood', 'group_peril': PRL_GRP_OO1},
    'flash flood': {'id': PRL_OSF, 'desc': 'Flash / Surface / Pluvial Flood', 'group_peril': PRL_GRP_OO1},
    'earthquake': {'id': PRL_QEQ, 'desc': 'Earthquake - Shake only', 'group_peril': PRL_GRP_QQ1},
    'fire following': {'id': PRL_QFF, 'desc': 'Fire Following', 'group_peril': PRL_GRP_QQ1},
    'liquefaction': {'id': PRL_QLF, 'desc': 'Liquefaction', 'group_peril': PRL_GRP_QQ1},
    'landslide': {'id': PRL_QLS, 'desc': 'Landslide', 'group_peril': PRL_GRP_QQ1},
    'sprinkler leakage': {'id': PRL_QSL, 'desc': 'Sprinkler Leakage', 'group_peril': PRL_GRP_QQ1},
    'tsunami': {'id': PRL_QTS, 'desc': 'Tsunami', 'group_peril': PRL_GRP_QQ1},
    'extra tropical cyclone': {'id': PRL_WEC, 'desc': 'Extra Tropical Cyclone', 'group_peril': PRL_GRP_WW2},
    'storm surge': {'id': PRL_WSS, 'desc': 'Storm Surge', 'group_peril': PRL_GRP_WW1},
    'tropical cyclone': {'id': PRL_WTC, 'desc': 'Tropical Cyclone', 'group_peril': PRL_GRP_WW2},
    'hail': {'id': PRL_XHL, 'desc': 'Hail', 'group_peril': PRL_GRP_XZ1},
    'lightning': {'id': PRL_XLT, 'desc': 'Lightning', 'group_peril': PRL_GRP_XX1},
    'convective wind': {'id': PRL_XSL, 'desc': 'Straight-line / other convective wind', 'group_peril': PRL_GRP_XX1},
    'tornado': {'id': PRL_XTD, 'desc': 'Tornado', 'group_peril': PRL_GRP_XX1},
    'freeze': {'id': PRL_ZFZ, 'desc': 'Freeze', 'group_peril': PRL_GRP_ZZ1},
    'ice': {'id': PRL_ZIC, 'desc': 'Ice', 'group_peril': PRL_GRP_ZZ1},
    'snow': {'id': PRL_ZSN, 'desc': 'Snow', 'eqv_oasis_peril': None, 'group_peril': PRL_GRP_ZZ1},
    'winterstorm wind': {'id': PRL_ZST, 'desc': 'Winterstorm Wind', 'group_peril': PRL_GRP_ZZ1}
})

# Path for storing static data/metadata files used in the package
STATIC_DATA_FP = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), '_data')

# Default profiles that describe the financial terms in the OED acc. and loc.
# (exposure) files, as well as how aggregation of FM input items is performed
# in the different OED FM levels


def get_default_accounts_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_acc_profile.json')
    return get_json(src_fp=fp) if not path else fp


def get_default_exposure_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_loc_profile.json')
    return get_json(src_fp=fp) if not path else fp


def get_default_unified_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_unified_profile.json')
    return get_json(src_fp=fp) if not path else fp


def get_default_fm_aggregation_profile(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'default_fm_agg_profile.json')
    return {int(k): v for k, v in get_json(src_fp=fp).items()} if not path else fp


def update_calc_rules():
    fp = os.path.join(STATIC_DATA_FP, 'calc_rules.csv')

    terms = ['deductible', 'deductible_min', 'deductible_max', 'limit', 'share', 'attachment']
    terms_indicators = ['{}_gt_0'.format(t) for t in terms]
    types_and_codes = ['deductible_type', 'deductible_code', 'limit_type', 'limit_code']

    dtypes = {
        'id_key': 'str',
        **{t: 'int32' for t in ['calcrule_id'] + terms_indicators + types_and_codes}
    }
    calc_rules = get_dataframe(
        src_fp=fp,
        col_dtypes=dtypes
    )

    calc_rules['id_key'] = [t for t in fast_zip_arrays(*calc_rules[terms_indicators + types_and_codes].transpose().values)]

    calc_rules.to_csv(path_or_buf=fp, index=False, encoding='utf-8')


# Ktools calc. rules
def get_calc_rules(path=False, update=False):
    fp = os.path.join(STATIC_DATA_FP, 'calc_rules.csv')
    if path:
        return fp

    if update:
        update_calc_rules()

    return get_dataframe(src_fp=fp)


# Default name prefixes of the Oasis input files (GUL + IL)
OASIS_FILES_PREFIXES = OrderedDict({
    'gul': {
        'complex_items': 'complex_items',
        'items': 'items',
        'coverages': 'coverages',
        'gulsummaryxref': 'gulsummaryxref'
    },
    'il': {
        'fm_policytc': 'fm_policytc',
        'fm_profile': 'fm_profile',
        'fm_programme': 'fm_programme',
        'fm_xref': 'fm_xref',
        'fmsummaryxref': 'fmsummaryxref'
    }
})


# Default analysis settings for deterministic loss generation
def get_default_deterministic_analysis_settings(path=False):
    fp = os.path.join(STATIC_DATA_FP, 'analysis_settings.json')
    return get_json(src_fp=fp) if not path else fp


# Ktools runtime parameters - defaults used during model execution
KTOOLS_NUM_PROCESSES = 2
KTOOLS_MEM_LIMIT = False
KTOOLS_FIFO_RELATIVE = False
KTOOLS_ALLOC_RULE = 2
KTOOLS_DEBUG = False
