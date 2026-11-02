"""Recognize the frozen municipal review protocol without relaxing other source gates."""
import copy
import importlib.util
from pathlib import Path
import unittest
SPEC=importlib.util.spec_from_file_location('queue_release_status',Path(__file__).with_name('review-salary-queue-release-v2.py'))
REVIEW=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(REVIEW)
class SourceAcceptanceProtocolTests(unittest.TestCase):
    def test_independently_accepted_scanned_municipal_protocol(self):
        good={'status':'accepted','verified':True,'sourceKind':'official-scanned-pdf'}
        REVIEW.verify_new_source_status('municipal',good)
        for field,value in [('status','held'),('verified',False),('verified',1),('sourceKind','compiled')]:
            bad=copy.deepcopy(good);bad[field]=value
            with self.subTest(field=field,value=value),self.assertRaises(AssertionError):REVIEW.verify_new_source_status('municipal',bad)
    def test_other_collections_require_their_exact_verified_protocol(self):
        for area in ['phsa','schools','acquisition']:
            REVIEW.verify_new_source_status(area,{'status':'verified','sourceKind':'official'})
            for bad in [{'status':'accepted','verified':True,'sourceKind':'official-scanned-pdf'},{'status':'held','sourceKind':'official'},{'status':'verified','sourceKind':'compiled'}]:
                with self.subTest(area=area,bad=bad),self.assertRaises(AssertionError):REVIEW.verify_new_source_status(area,bad)
if __name__=='__main__':unittest.main()
