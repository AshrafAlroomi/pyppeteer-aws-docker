import os
import uuid
from jinja2 import Environment, FileSystemLoader
from pyppeteer import launch
from PIL import Image, ImageDraw


class ImageBuilder:
    def __init__(self,
                 template_name: str,
                 directory: str = "/tmp",
                 html_element: str = ".post"):
        self.template_name = template_name
        self.html_element = html_element
        self.directory = directory

        os.makedirs(directory, exist_ok=True)

    async def build(self, context: dict, file_name: str = None) -> str:
        if not file_name:
            file_name = uuid.uuid4().hex[:10]
        template = self._get_template()
        content = template.render(context=context)
        html_file = os.path.join(self.directory, f"{file_name}.html")

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(content)

        image_file = os.path.join(self.directory, f"{file_name}.png")
        await self.take_screenshot(html_file, image_file)
        self.add_rounded_corners(image_path=image_file)

        return image_file

    def _get_template(self):
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        return env.get_template(self.template_name)

    @staticmethod
    async def take_screenshot(html_file: str, image_file: str):
        browser = await launch(headless=True, args=[
            "--no-sandbox",
            "--single-process",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-setuid-sandbox",
        ], executablePath=os.environ['CHROME_EXECUTABLE_PATH'], userDataDir="/tmp")

        page = await browser.newPage()
        await page.setViewport(
            {
                'width': 1280 * 2,
                'height': 720 * 2,
                'deviceScaleFactor': 2
            } # big image
        )
        file_url = f"file://{os.path.abspath(html_file)}"
        await page.goto(file_url)

        await page.waitForSelector(".post")
        post_element = await page.querySelector(".post")

        await post_element.screenshot({"path": image_file, 'omitBackground': True})
        await browser.close()

    @staticmethod
    def add_rounded_corners(image_path: str, radius: int = 40):
        """Load the PNG, add rounded corners, and save again."""
        img = Image.open(image_path).convert("RGBA")

        # Create a mask (same size) with black corners and white center
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius=radius, fill=255)

        # Apply the mask to the original (makes corners transparent)
        img.putalpha(mask)
        img.save(image_path)
