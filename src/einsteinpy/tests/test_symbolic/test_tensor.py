import numpy as np
import pytest
from sympy import Array, Function, cos, simplify, sin, symbols
from sympy.abc import y, z

from einsteinpy.symbolic.tensor import BaseRelativityTensor, Tensor


def schwarzschild_tensor():
    symbolstr = "t r theta phi"
    syms = symbols(symbolstr)
    G, M, c, a = symbols("G M c a")
    # using metric values of schwarschild space-time
    # a is schwarzschild radius
    list2d = np.zeros((4, 4), dtype=int).tolist()
    list2d[0][0] = 1 - (a / syms[1])
    list2d[1][1] = -1 / ((1 - (a / syms[1])) * (c ** 2))
    list2d[2][2] = -1 * (syms[1] ** 2) / (c ** 2)
    list2d[3][3] = -1 * (syms[1] ** 2) * (sin(syms[2]) ** 2) / (c ** 2)
    sch = Tensor(list2d)
    return sch


def arbitrary_tensor1():
    symbolstr = "x0 x1 x2 x3"
    syms = symbols(symbolstr)
    a, c = symbols("a c")
    f1, f2, f3 = Function("f1")(a, syms[2]), Function("f2")(c), Function("f3")
    list2d = np.zeros((4, 4), dtype=int).tolist()
    list2d[0][0] = 1 - (a * f1 / syms[1])
    list2d[1][1] = -1 / ((1 - (a / syms[1])) * (c ** 2))
    list2d[2][2] = -1 * (syms[1] ** 2) / (c ** 2)
    list2d[3][3] = -1 * (syms[1] ** 2) * (sin(syms[2]) ** 2) / (c ** 2)
    list2d[0][3] = list2d[3][0] = 5 * f2
    list2d[2][1] = list2d[1][2] = f3
    return BaseRelativityTensor(list2d, syms, config="ll"), [a, c], [f1, f2, f3]


def test_Tensor():
    x, y, z = symbols("x y z")
    test_list = [[[x, y], [y, sin(2 * z) - 2 * sin(z) * cos(z)]], [[z ** 2, x], [y, z]]]
    test_arr = Array(test_list)
    obj1 = Tensor(test_arr)
    obj2 = Tensor(test_list)
    assert obj1.tensor() == obj2.tensor()
    assert isinstance(obj1.tensor(), Array)
    assert obj1.simplify()[0, 1, 1] == 0


def test_Tensor_getitem():
    x, y, z = symbols("x y z")
    test_list = [[[x, y], [y, sin(2 * z) - 2 * sin(z) * cos(z)]], [[z ** 2, x], [y, z]]]
    obj = Tensor(test_list)
    n = 2
    for i in range(n ** 3):
        p, q, r = i % n, int(i / n) % n, int(i / n ** 2) % n
        assert obj[p, q, r] - test_list[p][q][r] == 0


def test_Tensor_str():
    x, y, z = symbols("x y z")
    test_list = [[[x, y], [y, x]], [[z, x], [y, z]]]
    obj1 = Tensor(test_list)

    assert "object at 0x" not in str(obj1)


def test_Tensor_repr():
    x, y, z = symbols("x y z")
    test_list = [[[x, y], [y, sin(2 * z) - 2 * sin(z) * cos(z)]], [[z ** 2, x], [y, z]]]
    obj1 = Tensor(test_list)

    machine_representation = repr(obj1)
    assert not "object at 0x" in machine_representation


def test_TypeError2():
    scht = schwarzschild_tensor().tensor()
    # pass non str object
    try:
        obj = Tensor(scht, config=0)
        assert False
    except TypeError:
        assert True


def test_TypeError3():
    scht = schwarzschild_tensor().tensor()
    # pass string containing elements other than 'l' or 'u'
    try:
        obj = Tensor(scht, config="al")
        assert False
    except TypeError:
        assert True


def test_subs_single():
    # replacing only schwarzschild radius(a) with 0
    T = schwarzschild_tensor()
    a, c = symbols("a c")
    test_arr = T.subs(a, 0)
    assert simplify(test_arr.arr[0, 0] - 1) == 0
    assert simplify(test_arr.arr[1, 1] - (-1 / c ** 2)) == 0


def test_subs_multiple():
    # replacing a with 0, c with 1
    # this should give a metric for spherical coordinates
    T = schwarzschild_tensor()
    a, c = symbols("a c")
    test_arr = T.subs([(a, 0), (c, 1)])
    assert simplify(test_arr.arr[0, 0] - 1) == 0
    assert simplify(test_arr.arr[1, 1] - (-1)) == 0


def test_check_properties():
    T = schwarzschild_tensor()
    assert T.order == T._order
    assert T.config == T._config


# tests for BaseRelativityTensor


def test_BaseRelativityTensor_automatic_calculation_of_free_variables():
    t1, variables, functions = arbitrary_tensor1()
    t2 = BaseRelativityTensor(
        t1.arr, t1.symbols(), config=t1.config, variables=variables, functions=functions
    )
    assert len(t1.variables) == len(t2.variables) and len(t1.variables) == len(
        variables
    )
    assert len(t1.functions) == len(t2.functions) and len(t1.functions) == len(
        functions
    )
    for v, f in zip(t1.variables, t1.functions):
        assert (
            (v in t2.variables)
            and (v in variables)
            and (f in t2.functions)
            and (f in functions)
        )


# tests fot Tensor Class to support scalars and sympy expression type scalars


@pytest.mark.parametrize("scalar", [11.89, y * z + 5])
def test_tensor_scalar(scalar):
    scalar_tensor = Tensor(scalar)
    assert scalar_tensor.tensor().rank() == 0
