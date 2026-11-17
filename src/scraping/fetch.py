"""Descarga moderada de HTML, validando primero robots.txt."""

from __future__ import annotations

import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from src.utils.logger import get_logger

USER_AGENT = (
    "GlobalDevelopmentAnalyticsAcademicProject/1.0 "
    "(educational, low-volume HTML table extraction)"
)
TIMEOUT = 20
MAX_RETRIES = 2
_LAST_REQUEST_AT: dict[str, float] = {}
LOGGER = get_logger()


class FetchError(RuntimeError):
    """Error de acceso permitido o validación de la página."""


def _polite_wait(url: str, interval: float = 2.0) -> None:
    host = urlparse(url).netloc
    elapsed = time.monotonic() - _LAST_REQUEST_AT.get(host, 0)
    if elapsed < interval:
        time.sleep(interval - elapsed)
    _LAST_REQUEST_AT[host] = time.monotonic()


def _check_robots(url: str, headers: dict, timeout: int) -> None:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    _polite_wait(robots_url)
    try:
        robots_response = requests.get(robots_url, headers=headers, timeout=timeout)
        robots_response.raise_for_status()
    except requests.RequestException as exc:
        LOGGER.error("No se pudo validar robots.txt (%s): %s", robots_url, exc)
        raise FetchError(f"No se pudo verificar robots.txt; scraping cancelado: {exc}") from exc
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_response.text.splitlines())
    if not parser.can_fetch(USER_AGENT, url):
        raise FetchError(f"robots.txt no autoriza el acceso automatizado a {url}")


def fetch_html(url: str, timeout: int = TIMEOUT, retries: int = MAX_RETRIES) -> str:
    """Fetch HTML only when robots.txt is reachable and permits this user agent.

    A robots.txt network error is treated as a denial; protections are never bypassed.
    """
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise FetchError(f"Solo se admiten URLs HTTPS públicas: {url}")
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    current_url = url
    checked_robots = {f"{parsed.scheme}://{parsed.netloc}"}
    _check_robots(current_url, headers, timeout)
    response = None
    redirects = 0
    attempt = 0
    while attempt <= retries:
        _polite_wait(current_url)
        try:
            response = requests.get(
                current_url, headers=headers, timeout=timeout, allow_redirects=False
            )
            if response.is_redirect or response.is_permanent_redirect:
                if redirects >= 5 or not response.headers.get("Location"):
                    raise FetchError("Demasiadas redirecciones o falta el destino de redirección")
                next_url = urljoin(current_url, response.headers["Location"])
                next_parsed = urlparse(next_url)
                if next_parsed.scheme != "https" or not next_parsed.netloc:
                    raise FetchError(f"Redirección no HTTPS rechazada: {next_url}")
                origin = f"{next_parsed.scheme}://{next_parsed.netloc}"
                if origin not in checked_robots:
                    _check_robots(next_url, headers, timeout)
                    checked_robots.add(origin)
                else:
                    _check_robots(next_url, headers, timeout)
                current_url = next_url
                redirects += 1
                continue
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "html" not in content_type.lower():
                raise FetchError(f"La respuesta no parece HTML: {content_type}")
            break
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "desconocido"
            LOGGER.error("HTTP %s al solicitar %s", status, current_url)
            if status in {401, 403, 404, 429}:
                raise FetchError(f"Acceso denegado o no disponible (HTTP {status}); no se reintentará") from exc
            if attempt >= retries:
                raise FetchError(f"Falló la solicitud HTTP tras {attempt + 1} intentos") from exc
        except FetchError:
            raise
        except requests.RequestException as exc:
            LOGGER.warning("Error transitorio en intento %s/%s: %s", attempt + 1, retries + 1, exc)
            if attempt >= retries:
                raise FetchError(f"Falló la solicitud tras {attempt + 1} intentos: {exc}") from exc
        attempt += 1
        time.sleep(2**attempt)
    assert response is not None
    soup = BeautifulSoup(response.text, "lxml")
    if not soup.find("table"):
        raise FetchError(f"No se encontraron etiquetas HTML <table> en {url}")
    return response.text
