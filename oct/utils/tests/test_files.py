import unittest2
import tempfile
import os

from oct.utils.files import (load_template,
                             get_directory_files,
                             get_directory_files_list,
                             remove_files,
                             move_file,
                             check_filename,
                             gen_digest,
                             copy_file,
                             gen_digest_path,
                             templater)


class TestFiles(unittest2.TestCase):

    def test_load_template(self):
        """Load template.
        """
        kwargs = {'template': 'test_template.t',
                  'base_dir': os.path.join('oct', 'utils', 'tests'),
                  'replace': 'REPLACED'}
        received = load_template(**kwargs)
        expected = 'Test Template REPLACED'
        msg = 'Template load error'
        self.assertEqual(received.rstrip(), expected, msg)

    def test_get_directory_files_no_directory(self):
        """Get directory file -- no directory.
        """
        dir = tempfile.mkdtemp()
        os.removedirs(dir)

        received = []
        for file in get_directory_files(dir):
            received.append(file)
        expected = []
        msg = 'Missing directory listing error'
        self.assertListEqual(received, expected, msg)

        received = get_directory_files_list(dir)
        expected = []
        msg = 'Missing directory listing error (list variant)'
        self.assertListEqual(received, expected, msg)

    def test_get_directory_files_no_files(self):
        """Get directory file -- no files.
        """
        dir = tempfile.mkdtemp()

        received = []
        for file in get_directory_files(dir):
            received.append(file)
        expected = []
        msg = 'Empty directory listing error'
        self.assertListEqual(received, expected, msg)

        received = get_directory_files_list(dir)
        expected = []
        msg = 'Empty directory listing error (list variant)'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        os.removedirs(dir)

    def test_get_directory_files(self):
        """Get directory files.
        """
        dir = tempfile.mkdtemp()
        file_obj = tempfile.NamedTemporaryFile(dir=dir)
        file = file_obj.name

        received = get_directory_files_list(dir)
        expected = [file]
        msg = 'Directory listing error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        file_obj.close()
        os.removedirs(dir)

    def test_get_directory_files_filtered(self):
        """Get directory files.
        """
        file_obj = tempfile.NamedTemporaryFile()
        dir = os.path.dirname(file_obj.name)
        file = file_obj.name

        filter_file = 'TCD_Deliveries_20140207111019.DAT'
        f = open(os.path.join(dir, filter_file), 'w')
        f.close()

        filter = 'TCD_Deliveries_\d{14}\.DAT'
        received = get_directory_files_list(os.path.dirname(file),
                                            filter=filter)
        expected = [os.path.join(dir, filter_file)]
        msg = 'Directory listing error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        remove_files(os.path.join(dir, filter_file))

    def test_check_filename(self):
        """Check T1250 filename format.
        """
        format = 'T1250_TOL.*\.txt'
        # Priority.
        received = check_filename('T1250_TOLP_20130904061851.txt', format)
        msg = 'Priority T1250 filename should validate True'
        self.assertTrue(received, msg)

        # Fast.
        received = check_filename('T1250_TOLF_VIC_20130904061851.txt',
                                  format)
        msg = 'Fast VIC T1250 filename should validate True'
        self.assertTrue(received, msg)

        # Dodgy.
        received = check_filename('T1250_dodgy_20130904061851.txt', format)
        msg = 'Dodgy filename should validate False'
        self.assertFalse(received, msg)

    def test_gen_digest_invalids(self):
        """Generate digest -- invalid value.
        """
        received = gen_digest(None)
        msg = 'Digest generation error -- None value'
        self.assertIsNone(received, msg)

        received = gen_digest(1234)
        msg = 'Digest generation error -- non-string value'
        self.assertIsNone(received, msg)

    def test_gen_digest(self):
        """Generate digest -- valid values.
        """
        received = gen_digest('193433')
        expected = '73b0b66e'
        msg = 'Digest generation error -- valid value'
        self.assertEqual(received, expected, msg)

    def test_create_digest_dir(self):
        """Create a digest-based directory.
        """
        received = gen_digest_path('193433')
        expected = ['73', '73b0', '73b0b6', '73b0b66e']
        msg = 'Digest directory path list error'
        self.assertListEqual(received, expected, msg)

    def test_copy_file(self):
        """Copy a file.
        """
        source_fh = tempfile.NamedTemporaryFile()
        fh = tempfile.NamedTemporaryFile()
        target = fh.name
        fh.close()

        # Check that the target does not exist.
        msg = 'Target file should not exist yet'
        self.assertFalse(os.path.exists(target))

        copy_file(source_fh.name, target)

        # Check that the target does exist.
        msg = 'Target file should exist '
        self.assertTrue(os.path.exists(target), msg)

        # Clean up.
        remove_files(target)
        source_fh.close()

    def test_templater(self):
        """Parse and substitute content-based template.
        """
        template_dir = os.path.join('oct', 'utils', 'tests', 'templates')
        template_file = 'email_body_html.t'
        path_to_template_file = os.path.join(template_dir, template_file)
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr',
             'err': '',
             'non_prod': ''}

        received = templater(path_to_template_file, **d)
        fh = open(os.path.join('oct',
                               'utils',
                               'tests',
                               'templates',
                               'email_body_html_template.t'))
        expected = fh.read().rstrip('\n')
        msg = 'Template string error'
        self.assertEqual(received, expected, msg)

    def test_templater_missing_template_dir(self):
        """Parse and substitute content-based template -- no template dir.
        """
        template_file = 'email_body_html.t'
        template_dir = tempfile.mkdtemp()
        path_to_template_file = os.path.join(template_dir, template_file)
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}

        received = templater(path_to_template_file, **d)
        msg = 'Template string error -- template path missing'
        self.assertIsNone(received, msg)

        # Clean up.
        os.rmdir(template_dir)

    def test_templater_incomplete_data(self):
        """Parse and substitute content-based template -- incomplete data.
        """
        template_dir = os.path.join('oct', 'templates')
        template_file = 'email_body_html.t'
        path_to_template_file = os.path.join(template_dir, template_file)

        # Key 'postcode' is missing.
        d = {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'connote_nbr': '218501217863-connote',
             'item_nbr': '3456789012-item_nbr'}

        received = templater(path_to_template_file, **d)
        msg = 'Template string error -- incomplete data'
        self.assertIsNone(received, msg)

    def test_move_file_to_current_directory(self):
        """Move a file into the current directory.
        """
        file_fh = tempfile.NamedTemporaryFile(delete=False)
        filename = file_fh.name

        received = move_file(filename, os.path.basename(filename))
        msg = 'Move file from current directory failed'
        self.assertTrue(received, msg)

        # Clean up.
        remove_files(os.path.basename(filename))

    def test_move_file_to_directory(self):
        """Move a file into a new directory.
        """
        target_dir = 'banana'
        file_fh = tempfile.NamedTemporaryFile(delete=False)
        filename = file_fh.name

        received = move_file(filename,
                             os.path.join(target_dir,
                                          os.path.basename(filename)))
        msg = 'Move file from current directory failed'
        self.assertTrue(received, msg)

        # Clean up.
        remove_files(get_directory_files_list('banana'))
        os.removedirs('banana')
