import os
import tempfile
from contextlib import contextmanager


@contextmanager
def tempfile_context() -> str:
    t_descriptor, t_path = tempfile.mkstemp()
    try:
        yield t_path
    except:
        pass
    finally:
        os.close(t_descriptor)
        os.unlink(t_path)
