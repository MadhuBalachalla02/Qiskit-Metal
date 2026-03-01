__copyright__ = "Copyright 2022-2025, Nanoacademic Technologies Inc."

"""
Maxwell eigenmode extraction for a meandered resonator device designed
using Qiskit Metal.
"""
from pathlib import Path
# Import Qiskit Metal.
from qiskit_metal import designs
from qiskit_metal.qlibrary.tlines.meandered import RouteMeander
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
# Import the QTCAD renderer.
from qiskit_metal.renderers.renderer_qtcad.qtcad_renderer import QQTCADRenderer

# Directories and file paths.
device_name = "resonator-eig"
# Work in the outputs folder of the current directory.
output_dir = str(Path(__file__).parent.resolve() / "output" / device_name)
# Geometry XAO file required for adaptive meshing.
geo_filepath = output_dir + "/" + device_name + ".xao"
# Mesh file.
mesh_filepath = output_dir + "/" + device_name + ".msh4"

# Whether to calculate the capacitance matrix using adaptive meshing.
adaptive = True
# Set minimum and maximum characteristic lengths for the mesh elements.
mesh_h_min = "150um"
mesh_h_max = "300um"


# Number of Maxwell eigenmodes.
num_modes = 3


# Instantiate a design object.
design = designs.MultiPlanar({}, True)
# We could specify the size of the silicon chip:
# design.chips.main.size["size_x"] = "3mm"
# design.chips.main.size["size_y"] = "3mm"

# Define terminations, one open and the other short to ground.
otg = OpenToGround(
    design,
    "open_to_ground",
    options=dict(pos_x="0.86mm", pos_y="0um", orientation="0"),
)
stg = ShortToGround(
    design,
    "short_to_ground",
    options=dict(pos_x="-0.86mm", pos_y="0um", orientation="180"),
)

# Create the resonator object `readout`, labelling the terminations (pins).
rt_meander = RouteMeander(
    design,
    "readout",
    dict(
        total_length="5.298mm",
        fillet="90um",
        lead=dict(start_straight="100um"),
        pin_inputs=dict(
            start_pin=dict(component="short_to_ground", pin="short"),
            end_pin=dict(component="open_to_ground", pin="open"),
        ),
    ),
)

open_pins = [("open_to_ground", "open")]


# Setting up the solver
qtcad_renderer = QQTCADRenderer(
    design,
    options=dict(
        adaptive=adaptive,
        output_dir=output_dir,
        mesh_scale=1e-3,
        adaptive_mesh_scale=1e-3,
        geo_filepath=geo_filepath,
        mesh_filepath=mesh_filepath,
        make_subdir=False,
        maxwell_emode=dict(
            num_modes=num_modes,
            tol_rel=0.05,
        ),
    ),
)

# Create the geometry from the design.
qtcad_renderer.render_design(
    open_pins=open_pins,
    # Do not mesh the device (yet).
    mesh_geoms=False,
    initial_mesh_h_min=mesh_h_min,
    initial_mesh_h_max=mesh_h_max,
)


# Mesh the device.
qtcad_renderer.gmsh.add_mesh(dim=3, intelli_mesh=not adaptive)

# Export the geometry and mesh files.
file_mesh, file_geo = qtcad_renderer.export_mesh()

# Export parameters.
qtcad_renderer.export_parameters()
# Run QTCAD to extract the Maxwell eigenmodes.
qtcad_renderer.run_qtcad("eigs")

frequencies = qtcad_renderer.load_qtcad_maxwell_eigenmodes()
print(frequencies)


qtcad_renderer.plot_eigenmodes()