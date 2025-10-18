import unittest, os, shutil
import main as module_to_test

class TestExcercise1(unittest.TestCase):
    unit_test_folder = os.path.join(module_to_test.save_path, 'unittest')

    @classmethod
    def setUpClass(self):
        if not os.path.exists(self.unit_test_folder):
            os.mkdir(self.unit_test_folder)
        # cleaning up test folder
        for f in os.listdir(self.unit_test_folder):
            file_path = os.path.join(self.unit_test_folder, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        module_to_test.save_path = self.unit_test_folder

    def test_worker_successfull(self):
        ix = module_to_test.download_uris.index('https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2018_Q4.zip')
        uri = module_to_test.download_uris[ix]
        module_to_test.worker(ix)
        file_list = os.listdir(module_to_test.save_path)
        self.assertTrue('Divvy_Trips_2018_Q4.csv' in file_list)

    def test_worker_404(self):
        ix = module_to_test.download_uris.index('https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip')
        uri = module_to_test.download_uris[ix]
        module_to_test.worker(ix)
        file_list = os.listdir(module_to_test.save_path)
        self.assertFalse('Divvy_Trips_2220_Q1.csv' in file_list)
    
    def test_cleaning(self):
        ix = module_to_test.download_uris.index('https://divvy-tripdata.s3.amazonaws.com/Divvy_Trips_2220_Q1.zip')
        uri = module_to_test.download_uris[ix]
        module_to_test.worker(ix)
        file_list = os.listdir(module_to_test.save_path)
        self.assertFalse('Divvy_Trips_2220_Q1.zip' in file_list)

    @classmethod
    def tearDownClass(self):
        print('Cleaning')
        # cleaning up test folder
        for f in os.listdir(self.unit_test_folder):
            file_path = os.path.join(self.unit_test_folder, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        # hard cleaning
        shutil.rmtree(self.unit_test_folder)


if __name__ == "__main__":
    unittest.main()