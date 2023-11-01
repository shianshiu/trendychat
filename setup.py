from setuptools import setup, find_packages

setup(
    name="trendychat",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # 列出您的包的依賴項
        "requests",
        # 'dependency2',
    ],
    # 其他的元數據：作者、授權、描述等
    author="Shawn Hsu",
    author_email="shianhian327@gmail.come",
    description="A trendy chat library for personal use.",
    keywords="chat communication",
)
