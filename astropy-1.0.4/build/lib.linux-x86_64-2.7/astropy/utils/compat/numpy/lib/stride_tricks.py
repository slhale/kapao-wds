# coding: utf-8
# Licensed like the corresponding numpy file; see licenses/NUMPY_LICENSE.rst
"""
Utilities that manipulate strides to achieve desirable effects.

An explanation of strides can be found in the "ndarray.rst" file in the
NumPy reference guide.

Notes
-----
The version provided here ensures broadcast_arrays passes on subclasses
if one sets ``subok=True``; see https://github.com/numpy/numpy/pull/4622

"""
from __future__ import division, absolute_import, print_function

import numpy as np

__all__ = ['broadcast_arrays', 'GE1P10']


def GE1P10(function=np.broadcast_arrays):
    """Test whether the broadcast_arrays function respects subclasses

    By default, ``np.broadcast_arrays`` is checked

    See https://github.com/numpy/numpy/pull/4622
    """

    class MySubClass(np.ndarray):
        pass

    try:
        return isinstance(function(MySubClass((1,)), subok=True)[0],
                          MySubClass)
    except TypeError:  # unexpected argument subok
        return False


if GE1P10():
    from numpy.lib.stride_tricks import broadcast_arrays

else:
    from numpy.lib.stride_tricks import DummyArray

    def as_strided(x, shape=None, strides=None, subok=False):
        """ Make an ndarray from the given array with the given shape and strides.
        """
        # first convert input to array, possibly keeping subclass
        x = np.array(x, copy=False, subok=subok)
        interface = dict(x.__array_interface__)
        if shape is not None:
            interface['shape'] = tuple(shape)
        if strides is not None:
            interface['strides'] = tuple(strides)
        array = np.asarray(DummyArray(interface, base=x))
        # Make sure dtype is correct in case of custom dtype
        if array.dtype.kind == 'V':
            array.dtype = x.dtype
        if type(x) is not type(array):
            # if input was an ndarray subclass and subclasses were OK,
            # then view the result as that subclass.
            array = array.view(type=type(x))
            # Since we have done something akin to a view from x, we should let
            # the subclass finalize (if it has it implemented, i.e., is not None).
            if array.__array_finalize__:
                array.__array_finalize__(x)
        return array

    def broadcast_arrays(*args, **kwargs):
        """
        Broadcast any number of arrays against each other.

        Parameters
        ----------
        `*args` : array_likes
            The arrays to broadcast.

        subok : bool, optional
            If True, then sub-classes will be passed-through, otherwise
            the returned arrays will be forced to be a base-class array (default).

        Returns
        -------
        broadcasted : list of arrays
            These arrays are views on the original arrays.  They are typically
            not contiguous.  Furthermore, more than one element of a
            broadcasted array may refer to a single memory location.  If you
            need to write to the arrays, make copies first.

        Examples
        --------
        >>> x = np.array([[1,2,3]])
        >>> y = np.array([[1],[2],[3]])
        >>> np.broadcast_arrays(x, y)
        [array([[1, 2, 3],
               [1, 2, 3],
               [1, 2, 3]]), array([[1, 1, 1],
               [2, 2, 2],
               [3, 3, 3]])]

        Here is a useful idiom for getting contiguous copies instead of
        non-contiguous views.

        >>> [np.array(a) for a in np.broadcast_arrays(x, y)]
        [array([[1, 2, 3],
               [1, 2, 3],
               [1, 2, 3]]), array([[1, 1, 1],
               [2, 2, 2],
               [3, 3, 3]])]

        """
        subok = kwargs.pop('subok', False)
        if kwargs:
            raise TypeError('broadcast_arrays() got an unexpected keyword '
                            'argument {}'.format(kwargs.pop()))
        args = [np.array(_m, copy=False, subok=subok) for _m in args]
        shapes = [x.shape for x in args]
        if len(set(shapes)) == 1:
            # Common case where nothing needs to be broadcasted.
            return args
        shapes = [list(s) for s in shapes]
        strides = [list(x.strides) for x in args]
        nds = [len(s) for s in shapes]
        biggest = max(nds)
        # Go through each array and prepend dimensions of length 1 to each of
        # the shapes in order to make the number of dimensions equal.
        for i in range(len(args)):
            diff = biggest - nds[i]
            if diff > 0:
                shapes[i] = [1] * diff + shapes[i]
                strides[i] = [0] * diff + strides[i]
        # Chech each dimension for compatibility. A dimension length of 1 is
        # accepted as compatible with any other length.
        common_shape = []
        for axis in range(biggest):
            lengths = [s[axis] for s in shapes]
            unique = set(lengths + [1])
            if len(unique) > 2:
                # There must be at least two non-1 lengths for this axis.
                raise ValueError("shape mismatch: two or more arrays have "
                    "incompatible dimensions on axis %r." % (axis,))
            elif len(unique) == 2:
                # There is exactly one non-1 length. The common shape will take
                # this value.
                unique.remove(1)
                new_length = unique.pop()
                common_shape.append(new_length)
                # For each array, if this axis is being broadcasted from a
                # length of 1, then set its stride to 0 so that it repeats its
                # data.
                for i in range(len(args)):
                    if shapes[i][axis] == 1:
                        shapes[i][axis] = new_length
                        strides[i][axis] = 0
            else:
                # Every array has a length of 1 on this axis. Strides can be
                # left alone as nothing is broadcasted.
                common_shape.append(1)

        # Construct the new arrays.
        broadcasted = [as_strided(x, shape=sh, strides=st, subok=subok)
                       for (x, sh, st) in zip(args, shapes, strides)]
        return broadcasted
