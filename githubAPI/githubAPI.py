import requests
import re


def convertToAPI(url: str) -> str:
    apiUrl = "https://api.github.com/repos/"
    url = url.split("/")
    api = apiUrl + url[3] + "/" + url[4]
    return api


def getLatestRelease(url: str) -> str:
    req = requests.get(f"{convertToAPI(url)}/releases/latest")
    return req.json()


def getLatestFile(asset: list, fileFormat: str):
    download_url: str = ''
    for name in asset:
        if name["browser_download_url"].endswith(fileFormat):
            download_url = name["browser_download_url"]
    return download_url


def validateGithubURL(url: str) -> bool:
    pattern = re.compile(
        r'^(https?:\/\/)?(www\.)?github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$')
    return bool(pattern.match(url))


def isLatestDownloadUrl(url: str, fileFormat: str, prevDownloadURL) -> bool:
    latestRelease = getLatestRelease(url)
    latestFile = getLatestFile(latestRelease['assets'], fileFormat)
    return latestFile == prevDownloadURL
