from pydra.compose import python
from fileformats.medimage import NiftiGz


@python.define
def smooth(in_file: NiftiGz, fwhm: float = 6.0) -> NiftiGz:
    """Gaussian spatial smoothing."""
    ...
    return out_file


from pydra.compose import shell
from fileformats.medimage import NiftiGz


@shell.define
class BET(shell.ShellDef["BET.Outputs"]):
    """FSL Brain Extraction Tool."""

    executable = "bet"
    in_file: NiftiGz
    frac_intensity: float = shell.arg(0.5)

    class Outputs(shell.ShellOutputs):
        out_file: NiftiGz
