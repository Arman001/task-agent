from langchain.tools import tool
import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import config


@tool
def calculator(expression: str) -> str:
    """Perform math calculations."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def text_analyzer(text: str) -> str:
    """Analyze text statistics."""
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines())

    return (
        f"Words: {words}\n"
        f"Characters: {chars}\n"
        f"Lines: {lines}"
    )


@tool
def file_reader(path: str) -> str:
    """Read file contents. Use simple filenames like 'test.txt' for current directory."""
    try:
        # Clean the path - remove any placeholder paths
        if path.startswith('/path/to/'):
            path = path.replace('/path/to/', '')
        # Use current directory for simple filenames
        if not os.path.dirname(path):
            path = os.path.join(os.getcwd(), path)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File content:\n{content}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def file_writer(path: str, content: str) -> str:
    """Write content to file. Use simple filenames like 'test.txt' for current directory."""
    try:
        # Clean the path - remove any placeholder paths
        if path.startswith('/path/to/'):
            path = path.replace('/path/to/', '')
        # Use current directory for simple filenames
        if not os.path.dirname(path):
            path = os.path.join(os.getcwd(), path)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {os.path.basename(path)}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def file_checker(path: str) -> str:
    """Check if file exists. Use simple filenames like 'test.txt' for current directory."""
    # Clean the path - remove any placeholder paths
    if path.startswith('/path/to/'):
        path = path.replace('/path/to/', '')
    # Use current directory for simple filenames
    if not os.path.dirname(path):
        path = os.path.join(os.getcwd(), path)
    exists = os.path.exists(path)
    return f"File {os.path.basename(path)} {'exists' if exists else 'does not exist'}"


# -------------------------
# Phase 3: Web Tools
# -------------------------

@tool
def web_search(query: str) -> str:
    """Search the internet. Input should be a search query string."""
    try:
        if not config.TAVILY_API_KEY:
            return "Error: TAVILY_API_KEY not configured"
        
        client = TavilyClient(api_key=config.TAVILY_API_KEY)
        response = client.search(query, max_results=3)
        
        results = []
        for i, result in enumerate(response.get('results', []), 1):
            title = result.get('title', 'No title')
            snippet = result.get('content', 'No description')
            url = result.get('url', '')
            results.append(f"{i}. {title}\n   {snippet}\n   URL: {url}")
        
        return "\n\n".join(results) if results else "No results found"
    except Exception as e:
        return f"Search error: {str(e)}"


@tool
def http_request(url: str, method: str = "GET") -> str:
    """Make HTTP GET or POST requests to REST APIs."""
    try:
        method = method.upper()
        if method not in ["GET", "POST"]:
            return "Error: Only GET and POST methods supported"
        
        if method == "GET":
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
        else:
            response = requests.post(url, timeout=config.REQUEST_TIMEOUT)
        
        response.raise_for_status()
        
        # Try to parse as JSON
        try:
            data = response.json()
            return f"Status: {response.status_code}\nData: {data}"
        except:
            return f"Status: {response.status_code}\nContent: {response.text[:500]}"
    except requests.Timeout:
        return "Error: Request timeout"
    except requests.RequestException as e:
        return f"HTTP error: {str(e)}"


@tool
def url_fetch(url: str) -> str:
    """Fetch and extract text content from a webpage."""
    try:
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit length
        return text[:2000] + "..." if len(text) > 2000 else text
    except Exception as e:
        return f"Fetch error: {str(e)}"


@tool
def api_weather(city: str) -> str:
    """Get current weather for a city. Input should be a city name like London or Paris."""
    try:
        if not config.OPENWEATHER_API_KEY:
            return "Error: OPENWEATHER_API_KEY not configured"
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        
        return f"Weather in {city}:\nTemperature: {temp}°C (feels like {feels_like}°C)\nConditions: {description}\nHumidity: {humidity}%"
    except requests.RequestException as e:
        return f"Weather API error: {str(e)}"
    except KeyError:
        return f"Error: Could not find weather data for '{city}'"
