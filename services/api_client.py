import os
import logging
import time
from typing import Optional, Dict, Union
import requests
import google.generativeai as genai
import re
import json
from tenacity import retry, stop_after_attempt, wait_fixed, stop_after_delay, retry_if_exception_type