"""
    pyexcel.io
    ~~~~~~~~~~~~~~~~~~~

    Uniform interface for reading/writing different excel file formats

    :copyright: (c) 2014-2015 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
from functools import partial
from .csvbook import CSVBook, CSVWriter
from .csvzipbook import CSVZipWriter, CSVZipBook
from .sqlbook import SQLBookReader, SQLBookWriter
from .djangobook import DjangoBookReader, DjangoBookWriter
from .._compact import is_string


FILE_FORMAT_CSV = 'csv'
FILE_FORMAT_TSV = 'tsv'
FILE_FORMAT_CSVZ = 'csvz'
FILE_FORMAT_TSVZ = 'tsvz'
FILE_FORMAT_ODS = 'ods'
FILE_FORMAT_XLS = 'xls'
FILE_FORMAT_XLSX = 'xlsx'
FILE_FORMAT_XLSM = 'xlsm'
FILE_FORMAT_SQL = 'sql'
FILE_FORMAT_DJANGO = 'django'


# A list of registered readers
READERS = {
    FILE_FORMAT_CSV: CSVBook,
    FILE_FORMAT_TSV: partial(CSVBook, dialect="excel-tab"),
    FILE_FORMAT_CSVZ: CSVZipBook,
    FILE_FORMAT_TSVZ: partial(CSVZipBook, dialect="excel-tab"),
    FILE_FORMAT_SQL: SQLBookReader,
    FILE_FORMAT_DJANGO: DjangoBookReader
}

ERROR_MESSAGE = "The plugin for file type %s is not installed. Please install %s"

AVAILABLE_READERS = {
    FILE_FORMAT_XLS: 'pyexcel-xls',
    FILE_FORMAT_XLSX: ('pyexcel-xls', 'pyexcel-xlsx'),
    FILE_FORMAT_XLSM: ('pyexcel-xls', 'pyexcel-xlsx'),
    FILE_FORMAT_ODS: ('pyexcel-ods', 'pyexcel-ods3')
}

# A list of registered writers
WRITERS = {
    FILE_FORMAT_CSV: CSVWriter,
    FILE_FORMAT_TSV: partial(CSVWriter, dialect="excel-tab"),
    FILE_FORMAT_CSVZ: CSVZipWriter,
    FILE_FORMAT_TSVZ: partial(CSVZipWriter, dialect="excel-tab"),
    FILE_FORMAT_SQL: SQLBookWriter,
    FILE_FORMAT_DJANGO: DjangoBookWriter
}

AVAILABLE_WRITERS = {
    FILE_FORMAT_XLS: 'pyexcel-xls',
    FILE_FORMAT_XLSX: 'pyexcel-xlsx',
    FILE_FORMAT_XLSM: 'pyexcel-xlsx',
    FILE_FORMAT_ODS: ('pyexcel-ods', 'pyexcel-ods3')
}

def list_readers():
    """list available readers"""
    print(READERS.keys())


def list_writers():
    """list available writers"""
    print(WRITERS.keys())


def resolve_missing_extensions(extension, available_list):
    handler = available_list.get(extension)
    message = ""
    if handler:
        if is_string(type(handler)):
            message = ERROR_MESSAGE % (extension, handler)
        else:
            merged = "%s or %s" % (handler[0], handler[1])
            message = ERROR_MESSAGE % (extension, merged)
        raise NotImplementedError(message)

def load_file(filename, sheet_name=None, sheet_index=None, **keywords):
    """Load data from any supported excel formats

    Tests:

        >>> import pyexcel as pe
        >>> pe.load("test.strange_type")
        Traceback (most recent call last):
            ...
        NotImplementedError: Cannot read content of file type strange_type from file test.strange_type
        >>> pe.load(("strange_type", "fake io"))
        Traceback (most recent call last):
            ...
        NotImplementedError: Cannot read content of file type strange_type from stream
        >>> pe.load("test.ods")
        Traceback (most recent call last):
            ...
        NotImplementedError: The plugin for file type ods is not installed. Please install pyexcel-ods or pyexcel-ods3
        >>> pe.load(("ods", "fake io"))
        Traceback (most recent call last):
            ...
        NotImplementedError: The plugin for file type ods is not installed. Please install pyexcel-ods or pyexcel-ods3
    
    """
    extension = None
    book = None
    from_memory = False
    content = None
    if filename in READERS:
        book_class = READERS[filename]
        book = book_class(**keywords)
    else:
        if isinstance(filename, tuple):
            from_memory = True
            extension = filename[0]
            content = filename[1]
        elif is_string(type(filename)):
            extension = filename.split(".")[-1]
        else:
            raise IOError("cannot handle unknown content")
        if extension in READERS:
            book_class = READERS[extension]
            if from_memory: 
                book = book_class(None, file_content=content,
                                  load_sheet_with_name=sheet_name,
                                  load_sheet_at_index=sheet_index,
                                  **keywords)
            else:
                book = book_class(filename,
                                  load_sheet_with_name=sheet_name,
                                  load_sheet_at_index=sheet_index,
                                  **keywords)
        else:
            resolve_missing_extensions(extension, AVAILABLE_READERS)
            if from_memory:
                raise NotImplementedError("Cannot read content of file type %s from stream" % filename[0])
            else:
                raise NotImplementedError("Cannot read content of file type %s from file %s" % (extension, filename))
    return book


def get_writer(filename, **keywords):
    """Create a writer from any supported excel formats

    Tests:

        >>> import pyexcel as pe
        >>> data = [[1,2]]
        >>> sheet = pe.Sheet(data)
        >>> sheet.save_as("test.strange_type")
        Traceback (most recent call last):
            ...
        NotImplementedError: Cannot write content of file type strange_type to file test.strange_type
        >>> sheet.save_to_memory("strange_type", "fake io")
        Traceback (most recent call last):
            ...
        NotImplementedError: Cannot write content of file type strange_type to stream
        >>> sheet.save_as("test.ods")
        Traceback (most recent call last):
            ...
        NotImplementedError: The plugin for file type ods is not installed. Please install pyexcel-ods or pyexcel-ods3
        >>> sheet.save_to_memory("ods", "fake io")
        Traceback (most recent call last):
            ...
        NotImplementedError: The plugin for file type ods is not installed. Please install pyexcel-ods or pyexcel-ods3
        
    """
    extension = None
    writer = None
    to_memory = False
    if filename in WRITERS:
        writer_class = WRITERS[filename]
        writer = writer_class(filename, **keywords)
    else:
        if isinstance(filename, tuple):
            extension = filename[0]
            to_memory = True
        elif is_string(type(filename)):
            extension = filename.split(".")[-1]
        else:
            raise IOError("cannot handle unknown content")
        if extension in WRITERS:
            writer_class = WRITERS[extension]
            if to_memory:
                writer = writer_class(filename[1], **keywords)
            else:
                writer = writer_class(filename, **keywords)
        else:
            resolve_missing_extensions(extension, AVAILABLE_WRITERS)
            if to_memory:
                raise NotImplementedError("Cannot write content of file type %s to stream" % filename[0])
            else:
                raise NotImplementedError("Cannot write content of file type %s to file %s" % (extension, filename))
    return writer

