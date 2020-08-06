"""
A faster nbconvert script based on the difference
versus a previous run.

For robustness, does *not* use inotify. (Works around
problems like inode limits on Kubernetes clusters.)
"""

import difflib
import hashlib
import pathlib
import copy
from pathlib import Path

import nbconvert


def hash_cell_repr(cell):
    """
    Create a string representation of the given cell
    (a dictionary), ensuring the keys are sorted first.
    """
    sorted_keys = sorted(cell.keys())
    sorted_cell = {key: cell[key] for key in sorted_keys}
    cell_hash = repr(sorted_cell)
    return cell_hash


def hash_cell(cell, hash_alg='md5'):
    """
    Hashes a byte-string representation of the given cell
    (a dictionary), ensuring the keys are sorted first.
    """
    cell_bytes = hash_cell_repr(cell).encode('utf8')
    alg = getattr(hashlib, hash_alg)
    return alg(cell_bytes).hexdigest()


# def hash_all_cells_repr(cells):
#     """
#     Hash the given list of cells, returning a list of hashes.
#     """
#     return [hash_cell_repr(cell) for cell in cells]


def hash_all_cells(cells, hash_alg='md5'):
    """
    Hash the given list of cells, returning a list of hashes.
    """
    return [hash_cell(cell, hash_alg=hash_alg) for cell in cells]


def notebook_to_metadata(filename):
    """
    Read the given .ipynb file and return a dictionary with these keys:
    
    'path': file path
    'mod_time': file modification time at last read
    'size': size in bytes at last read
    'cell_hashes': list of hashes of each cell
    """
    path = Path(filename)
    contents = path.read_text()
    try:
        nb = nbformat.reads(contents, as_version=nbformat.NO_CONVERT)
    except Exception as e:
        data = {'error': str(e)}
    else:
        data = {'path': str(path),
                'mod_time': os.path.getmtime(path),
                'size': os.path.getsize(path),
                'cell_hashes': hash_all_cells(nb.cells)}
    return data


def get_diff_opcodes(nb1_cell_hashes, nb2_cell_hashes):
    """
    Apply the SequenceMatcher to return op codes
    for converting notebook 1 into notebook 2.
    """
    m = difflib.SequenceMatcher(a=nb1_cell_hashes,
                                b=nb1_cell_hashes)
    return m.get_opcodes()


def patch(diff_opcodes, a, b):
    """
    A prototype. Not useful by itself.
    
    Transform a into b by using the given opcodes.
    """
    
    c = a.copy()
    offset = 0

    for (opcode, i1, i2, j1, j2) in diff_opcodes:
        print(c)
        c[i1+offset:i2+offset] = b[j1:j2]
        offset += (j2-j1) - (i2-i1)
    
    assert b == c
    return c


# Example:
# a = list("qabxcd")
# b = list("abycdf")

# test_matcher = difflib.SequenceMatcher(a=a, b=b)
# opcodes = test_matcher.get_opcodes()
# opcodes

# c = patch(opcodes, a, b)




def patch_transform(diff_opcodes,
                    a_transformed,
                    b_raw,
                    transform,
                    verify=False):
    """
    Minimally patch the list
    
    a_transformed == [transform(ai) for ai in a_raw]
    
    into the list
    
    b_transformed == [transform(bi) for bi in b_raw]
    
    by using the given opcodes returned by the
    get_opcodes() method of a 
    difflib.SequenceMatcher between a_raw and b_raw.
    
    a_raw is not needed.
    
    If transform is passed (as a function), applies
    the transform function to each item in a first.
    
    The assumption is that the transform function is expensive
    and/or the diff is small relative to the size of b_raw.
    
    The goal is to save time versus applying transform() to every
    item in b_raw.
    """
    
    c_transformed = a_transformed.copy()
    offset = 0

    for (opcode, i1, i2, j1, j2) in diff_opcodes:
        new = [transform(cell) for cell in b_raw[j1:j2]]
        c_transformed[i1+offset:i2+offset] = new
        offset += (j2-j1) - (i2-i1)
    
    if verify:
        assert [transform(bi) for bi in b_raw] == c_transformed
    
    return c_transformed


# TODO: now apply this to create a differential nbconvert function

def differential_nbconvert(diff_opcodes,
                           old_converted_cells,
                           new_cells):
    """
    TODO: FIXME 
    """
    pass
