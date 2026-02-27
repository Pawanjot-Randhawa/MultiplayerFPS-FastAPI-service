import base64

import cv2
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv

load_dotenv()


def _prepare_image_data_url(image_bytes: bytes, size: int = 256, jpeg_quality: int = 75) -> str:
    if not image_bytes:
        raise ValueError("image_bytes cannot be empty")

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    decoded_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if decoded_image is None:
        raise ValueError("Invalid image bytes: unable to decode image")

    resized_image = cv2.resize(decoded_image, (size, size), interpolation=cv2.INTER_AREA)
    encoded_ok, encoded_image = cv2.imencode(
        ".jpg",
        resized_image,
        [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
    )

    if not encoded_ok:
        raise ValueError("Failed to encode resized image")

    encoded_b64 = base64.b64encode(encoded_image.tobytes()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded_b64}"


def filter_image_bytes_gemini(image_bytes: bytes) -> str:
    image_data_url = _prepare_image_data_url(image_bytes, size=256, jpeg_quality=75)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    response = llm.invoke(
        [
            HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": (
                            "You are an image analysis assistant that detects potential cheating in game screenshots. "
                            "You are specifically looking for wall hacks, indicated by unnatural outlines around "
                            "players or objects that should be hidden. "
                            "Return only one word: 'cheater' or 'fair'."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url},
                    },
                ]
            )
        ]
    )
    return response.content.strip().lower()