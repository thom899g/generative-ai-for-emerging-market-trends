"""
Firebase client for state management, model persistence, and real-time updates.
Implements retry logic, batch operations, and connection pooling.
"""
import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Dict, Any, List, Optional, Union
import logging
import json
import time
from datetime import datetime, timedelta
from dataclasses import asdict, is_dataclass
import numpy as np