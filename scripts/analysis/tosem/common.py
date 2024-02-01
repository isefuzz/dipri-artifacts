import matplotlib
import matplotlib.pyplot as plt

# To avoid type-3 font error
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
plt.rcParams['font.size'] = 16

fuzzers = [
    # Baselines
    'aflpp', 'aflpp-Z',
    # For ablation experiment
    'dipri',
    'dipri-cov', 'dipri-depth', 'dipri-handicap',
    'dipri-len', 'dipri-time',  'dipripp',
    # For config experiment
    'dipri-AE', 'dipri-AH',
    'dipri-PE', 'dipri-PH',
    'dipri-VE', 'dipri-VH',
    # For comparison experiment
    'alphuzz', 'k-scheduler',
]

targets = [
    'cxxfilt', 'nm-new', 'objdump', 'readelf',
    'djpeg', 'mjs', 'mutool', 'xmllint',
]

targets_fb = [
    'bloaty_fuzz_target', 'curl_curl_fuzzer_http',
    'freetype2_ftfuzzer', 'jsoncpp_jsoncpp_fuzzer',
    'lcms_cms_transform_fuzzer', 'libpcap_fuzz_both',
    're2_fuzzer', 'sqlite3_ossfuzz',
]

targets_zest = [
    'ant', 'bcel', 'chess', 'closure', 'rhino'
]

# Color setting
colors = {
    # Baselines
    'afl': 'gray',
    'aflpp': 'royalblue',
    'aflpp-Z': 'orange',
    # Fuzzbench
    'aflplusplus_406': 'royalblue',
    'aflplusplus_406_z': 'orange',
    'aflplusplus_406_dipri_ah': 'purple',
    'aflplusplus_406_dipri_vh': 'red',
    # Ablation
    'dipri': 'red',
    'dipri-cov': 'green',
    'dipri-depth': 'peru',
    'dipri-handicap': 'firebrick',
    'dipri-len': 'cyan',
    'dipri-time': 'gold',
    'dipripp': 'black',
    # JAva
    'zest': 'gray',
    # Configuration
    'dipri-AE': 'hotpink',
    'dipri-AH': 'purple',
    'dipri-PE': 'gold',
    'dipri-PH': 'cyan',
    'dipri-VE': 'green',
    'dipri-VH': 'red',
    # Comparison,
    'alphuzz': 'cyan',
    'k-scheduler': 'gold',
}


def output_fig(figure: plt.Figure, path: str, tight: bool = True):
    if tight:
        figure.tight_layout()
    figure.savefig(path)
    print('[LOG] Output to:', path)
    plt.close()

