# tests/unit/test_csvdatareader.py
from recipe.adapters.datareader.csvdatareader import CSVDataReader



def test_csv_reader_initialization():
    reader = CSVDataReader("test.csv")
    assert reader._CSVDataReader__csv_filename == "test.csv"
    assert len(reader.recipes) == 0


def test_csv_reader_properties():
    reader = CSVDataReader("test.csv")
    assert reader.recipes == []
    assert reader.authors == []
    assert reader.categories == []


def test_get_create_author():
    reader = CSVDataReader("test.csv")
    author1 = reader._get_create_author(1, "Chef A")
    author2 = reader._get_create_author(1, "Chef A")  # Same ID

    assert author1 == author2  # Should return same author
    assert author1.name == "Chef A"


def test_get_create_category():
    reader = CSVDataReader("test.csv")
    cat1 = reader._get_create_category("Italian")
    cat2 = reader._get_create_category("Italian")  # Same name

    assert cat1 == cat2  # Should return same category
    assert cat1.name == "Italian"