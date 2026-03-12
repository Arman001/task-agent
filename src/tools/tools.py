from langchain.tools import tool
import os
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from src.core import config
from src.memory.manager import MemoryManager
import hashlib
import subprocess

memory_manager = MemoryManager()


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
            
        # Cache file metadata
        file_size = os.path.getsize(path)
        lines = content.count('\n') + 1
        words = len(content.split())
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        memory_manager.cache_file_metadata(
            path=path,
            size=file_size,
            line_count=lines,
            word_count=words,
            content_hash=content_hash
        )
        
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
            
        # Cache file metadata
        file_size = os.path.getsize(path)
        lines = content.count('\n') + 1
        words = len(content.split())
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        memory_manager.cache_file_metadata(
            path=path,
            size=file_size,
            line_count=lines,
            word_count=words,
            content_hash=content_hash
        )
        
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


@tool
def file_deleter(path: str) -> str:
    """Delete a file. Use simple filenames like 'test.txt' for current directory."""
    try:
        # Clean the path - remove any placeholder paths
        if path.startswith('/path/to/'):
            path = path.replace('/path/to/', '')
        # Use current directory for simple filenames
        if not os.path.dirname(path):
            path = os.path.join(os.getcwd(), path)
        if os.path.exists(path):
            os.remove(path)
            return f"Successfully deleted {os.path.basename(path)}"
        else:
            return f"Error: File {os.path.basename(path)} not found"
    except Exception as e:
        return f"Error deleting file: {e}"


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

# -------------------------
# Phase 6: Code Execution
# -------------------------

@tool
def python_executor(code: str) -> str:
    """Executes Python code and returns the output. Use this for:
- Data analysis and statistics
- Creating charts and visualizations
- Complex calculations
- File processing with Python libraries

The code should be valid Python. Available libraries: os, sys, json, csv, 
pandas, numpy, matplotlib (if installed).
CRITICAL: If using pandas/matplotlib for plotting data provided in the prompt, DO NOT attempt to read from a non-existent file like 'sales_data.csv'. Directly hardcode the array/list of data into the python script!
CRITICAL: If using matplotlib to generate charts, ALWAYS use `plt.savefig('filename.png')` BEFORE calling `plt.show()`. Calling plt.show() first clears the figure, resulting in a blank saved image. Alternatively, omit plt.show() completely when saving files."""
    try:
        if not getattr(config, 'ENABLE_CODE_EXECUTION', True):
            return "Error: Code execution is disabled in config."
            
        files_before = set(os.listdir(os.getcwd()))
        
        with open(".temp_exec.py", "w", encoding="utf-8") as f:
            f.write(code)
            
        result = subprocess.run(
            ["python3", ".temp_exec.py"],
            capture_output=True,
            text=True,
            timeout=getattr(config, 'CODE_EXECUTION_TIMEOUT', 30),
            cwd=os.getcwd()
        )
        
        files_after = set(os.listdir(os.getcwd()))
        generated = list(files_after - files_before)
        if ".temp_exec.py" in generated:
            generated.remove(".temp_exec.py")
            
        if os.path.exists(".temp_exec.py"):
            os.remove(".temp_exec.py")
            
        output_str = ""
        if result.returncode == 0:
            output_str += "Execution Status: Success\n"
        else:
            output_str += "Execution Status: Error\n"
            
        if result.stdout:
            output_str += f"Stdout:\n{result.stdout}\n"
        if result.stderr:
            output_str += f"Stderr:\n{result.stderr}\n"
            
        if generated:
            output_str += f"Files Generated: {', '.join(generated)}\n"
            
        return output_str.strip() or "Code executed successfully with no output."
            
    except subprocess.TimeoutExpired:
        if os.path.exists(".temp_exec.py"):
            os.remove(".temp_exec.py")
        return "Execution Error: Code execution timed out after 30s"
    except Exception as e:
        if os.path.exists(".temp_exec.py"):
            os.remove(".temp_exec.py")
        return f"Execution Error: {str(e)}"
