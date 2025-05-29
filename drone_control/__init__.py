# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "drone_control",
    "author" : "Alberto Ramos Sánchez",
    "description" : "",
    "blender" : (4, 0, 0),
    "version" : (1, 0, 0),
    "location" : "View3D > Sidebar Panel > Drone Control Panel",
    "warning" : "",
    "category" : "Scene",
    "wiki_url": ""
}

from . import auto_load

auto_load.init()

def init_log():
    import logging
    from pathlib import Path
    import datetime

    path = Path.home() / Path("BlenderLog")
    path.mkdir(exist_ok=True, parents=True)

    logfile = path / Path(datetime.datetime.now().strftime("log_%m%d%Y_%H%M%S") +".log")

    logger = logging.getLogger("myblenderlog")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", '%Y-%m-%d %H:%M:%S')

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

def register():
    init_log()
    
    auto_load.register()

def unregister():
    auto_load.unregister()
