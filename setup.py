from setuptools import setup, find_packages

setup(
    name="trendychat",
    version="0.5",
    packages=find_packages(),
    install_requires=[
        "langchain==0.0.314",
        "openai==0.28.1",
        "pymongo==4.5.0",
        "unstructured==0.10.22",
        "unstructured[docx]",
        # "unstructured[pdf]",
        "azure-core==1.29.4",
        "azure-storage-blob==12.18.3",
        "tiktoken==0.5.1",
        "pytz==2023.3.post1",
        "python-dotenv==1.0.0",
        "tqdm==4.66.1",
    ],
    # 其他的元數據：作者、授權、描述等
    author="Shawn Hsu",
    author_email="shianhian327@gmail.come",
    description="A trendy chat library for personal use.",
    keywords="chat communication",
)
