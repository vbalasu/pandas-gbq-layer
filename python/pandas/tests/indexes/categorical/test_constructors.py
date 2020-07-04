import numpy as np
import pytest

from pandas import Categorical, CategoricalDtype, CategoricalIndex, Index
import pandas._testing as tm


class TestCategoricalIndexConstructors:
    def test_construction(self):

        ci = CategoricalIndex(list("aabbca"), categories=list("abcd"), ordered=False)
        categories = ci.categories

        result = Index(ci)
        tm.assert_index_equal(result, ci, exact=True)
        assert not result.ordered

        result = Index(ci.values)
        tm.assert_index_equal(result, ci, exact=True)
        assert not result.ordered

        # empty
        result = CategoricalIndex(categories=categories)
        tm.assert_index_equal(result.categories, Index(categories))
        tm.assert_numpy_array_equal(result.codes, np.array([], dtype="int8"))
        assert not result.ordered

        # passing categories
        result = CategoricalIndex(list("aabbca"), categories=categories)
        tm.assert_index_equal(result.categories, Index(categories))
        tm.assert_numpy_array_equal(
            result.codes, np.array([0, 0, 1, 1, 2, 0], dtype="int8")
        )

        c = Categorical(list("aabbca"))
        result = CategoricalIndex(c)
        tm.assert_index_equal(result.categories, Index(list("abc")))
        tm.assert_numpy_array_equal(
            result.codes, np.array([0, 0, 1, 1, 2, 0], dtype="int8")
        )
        assert not result.ordered

        result = CategoricalIndex(c, categories=categories)
        tm.assert_index_equal(result.categories, Index(categories))
        tm.assert_numpy_array_equal(
            result.codes, np.array([0, 0, 1, 1, 2, 0], dtype="int8")
        )
        assert not result.ordered

        ci = CategoricalIndex(c, categories=list("abcd"))
        result = CategoricalIndex(ci)
        tm.assert_index_equal(result.categories, Index(categories))
        tm.assert_numpy_array_equal(
            result.codes, np.array([0, 0, 1, 1, 2, 0], dtype="int8")
        )
        assert not result.ordered

        result = CategoricalIndex(ci, categories=list("ab"))
        tm.assert_index_equal(result.categories, Index(list("ab")))
        tm.assert_numpy_array_equal(
            result.codes, np.array([0, 0, 1, 1, -1, 0], dtype="int8")
        )
        assert not result.ordered

        result = CategoricalIndex(ci, categories=list("ab"), ordered=True)
        tm.assert_index_equal(result.categories, Index(list("ab")))
        tm.assert_numpy_array_equal(
            result.codes, np.array([0, 0, 1, 1, -1, 0], dtype="int8")
        )
        assert result.ordered

        result = CategoricalIndex(ci, categories=list("ab"), ordered=True)
        expected = CategoricalIndex(
            ci, categories=list("ab"), ordered=True, dtype="category"
        )
        tm.assert_index_equal(result, expected, exact=True)

        # turn me to an Index
        result = Index(np.array(ci))
        assert isinstance(result, Index)
        assert not isinstance(result, CategoricalIndex)

    def test_construction_with_dtype(self):

        # specify dtype
        ci = CategoricalIndex(list("aabbca"), categories=list("abc"), ordered=False)

        result = Index(np.array(ci), dtype="category")
        tm.assert_index_equal(result, ci, exact=True)

        result = Index(np.array(ci).tolist(), dtype="category")
        tm.assert_index_equal(result, ci, exact=True)

        # these are generally only equal when the categories are reordered
        ci = CategoricalIndex(list("aabbca"), categories=list("cab"), ordered=False)

        result = Index(np.array(ci), dtype="category").reorder_categories(ci.categories)
        tm.assert_index_equal(result, ci, exact=True)

        # make sure indexes are handled
        expected = CategoricalIndex([0, 1, 2], categories=[0, 1, 2], ordered=True)
        idx = Index(range(3))
        result = CategoricalIndex(idx, categories=idx, ordered=True)
        tm.assert_index_equal(result, expected, exact=True)

    def test_construction_empty_with_bool_categories(self):
        # see GH#22702
        cat = CategoricalIndex([], categories=[True, False])
        categories = sorted(cat.categories.tolist())
        assert categories == [False, True]

    def test_construction_with_categorical_dtype(self):
        # construction with CategoricalDtype
        # GH#18109
        data, cats, ordered = "a a b b".split(), "c b a".split(), True
        dtype = CategoricalDtype(categories=cats, ordered=ordered)

        result = CategoricalIndex(data, dtype=dtype)
        expected = CategoricalIndex(data, categories=cats, ordered=ordered)
        tm.assert_index_equal(result, expected, exact=True)

        # GH#19032
        result = Index(data, dtype=dtype)
        tm.assert_index_equal(result, expected, exact=True)

        # error when combining categories/ordered and dtype kwargs
        msg = "Cannot specify `categories` or `ordered` together with `dtype`."
        with pytest.raises(ValueError, match=msg):
            CategoricalIndex(data, categories=cats, dtype=dtype)

        with pytest.raises(ValueError, match=msg):
            Index(data, categories=cats, dtype=dtype)

        with pytest.raises(ValueError, match=msg):
            CategoricalIndex(data, ordered=ordered, dtype=dtype)

        with pytest.raises(ValueError, match=msg):
            Index(data, ordered=ordered, dtype=dtype)

    def test_create_categorical(self):
        # GH#17513 The public CI constructor doesn't hit this code path with
        # instances of CategoricalIndex, but we still want to test the code
        ci = CategoricalIndex(["a", "b", "c"])
        # First ci is self, second ci is data.
        result = CategoricalIndex._create_categorical(ci, ci)
        expected = Categorical(["a", "b", "c"])
        tm.assert_categorical_equal(result, expected)
