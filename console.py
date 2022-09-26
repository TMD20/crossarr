from rich.console import Console
from rich.style import Style
from rich.panel import Panel
from rich.progress import Progress,TextColumn,BarColumn,TaskProgressColumn
from rich.status import Status
from rich.console import Group
from rich.live import Live
from rich.table import Column,Table
from rich.layout import Layout
from rich import print


name_column = TextColumn("{task.name}", table_column=Column(ratio=1))
desc_column = TextColumn("{task.description}", table_column=Column(ratio=1))
progressTable = Progress(name_column, desc_column, expand=True)

mainConsole= Console()



error_style = Style(color="red", blink=True, bold=True)
normal_header_style = Style(color="green", blink=False, bold=True)
normal_style = Style(color="magenta")


#logging
import logging







        