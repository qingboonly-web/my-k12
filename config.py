# SheerID 教师验证配置文件

# SheerID API 配置
PROGRAM_ID = '68d47554aa292d20b9bec8f7'
SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# 文件大小限制
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB

# 学校配置（高中）
SCHOOLS = {
    '10148750': {
        "id": 10148750,
        "idExtended": "10148750",
        "name": "Dr. Ronald E. Mcnair Junior High",
        "city": "Pearland",
        "state": "TX",
        "country": "US",
        "type": "K12",
        "latitude": 29.55716435,
        "longitude": -95.419651462316
    },
}

# 默认学校
DEFAULT_SCHOOL_ID = '10148750'


