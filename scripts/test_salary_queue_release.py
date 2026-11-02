"""Explicit root-revision selection must never silently reuse a superseded draft."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC=importlib.util.spec_from_file_location('queue_release_review',Path(__file__).with_name('review-salary-queue-release.py'))
REVIEW=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(REVIEW)

class RootReleaseSelectionTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name);self.out=self.root/'research/salaries/queue-completion-2026-11-01';self.out.mkdir(parents=True)
        self.root_patch=patch.object(REVIEW,'ROOT',self.root);self.out_patch=patch.object(REVIEW,'OUT',self.out)
        self.root_patch.start();self.out_patch.start();self.addCleanup(self.root_patch.stop);self.addCleanup(self.out_patch.stop)
        self.previous=self.save('parent-acceptance.json',{'accepted':True,'noOutreach':True})
        self.current={'accepted':True,'rootReleaseFreezeFile':'integration/candidate-freeze-v2.json','supersededPrepublicationParentAcceptance':self.previous}
        self.current_ref=self.save('parent-acceptance-v2.json',self.current)
        self.selection={'schema':'salary-queue-parent-selection-v1','selectedVersion':2,'effectiveParentAcceptance':self.current_ref,'supersededPrepublicationParentAcceptance':self.previous}
        self.save('parent-acceptance-selection.json',self.selection)
    def save(self,name,document):
        path=self.out/name;raw=(json.dumps(document,indent=2)+'\n').encode();path.write_bytes(raw)
        return {'path':str(path.relative_to(self.root)),'sha256':hashlib.sha256(raw).hexdigest()}
    def test_explicit_reviewed_revision_is_selected(self):
        self.assertEqual(REVIEW.current_parent_acceptance(),self.current)
    def test_missing_selector_does_not_fall_back_to_existing_old_acceptance(self):
        (self.out/'parent-acceptance-selection.json').unlink()
        with self.assertRaises(FileNotFoundError):REVIEW.current_parent_acceptance()
    def test_wrong_revision_or_old_receipt_is_rejected(self):
        for value in [True,1,'2',None,3]:
            with self.subTest(value=value):
                self.selection['selectedVersion']=value;self.save('parent-acceptance-selection.json',self.selection)
                with self.assertRaises(AssertionError):REVIEW.current_parent_acceptance()
        self.selection['selectedVersion']=2;self.selection['effectiveParentAcceptance']=self.previous;self.save('parent-acceptance-selection.json',self.selection)
        with self.assertRaises(AssertionError):REVIEW.current_parent_acceptance()
    def test_tampered_receipt_or_original_history_cannot_be_selected(self):
        for field in ['effectiveParentAcceptance','supersededPrepublicationParentAcceptance']:
            original=self.selection[field];self.selection[field]={**original,'sha256':'0'*64};self.save('parent-acceptance-selection.json',self.selection)
            with self.subTest(field=field),self.assertRaises(AssertionError):REVIEW.current_parent_acceptance()
            self.selection[field]=original
        self.current['rootReleaseFreezeFile']='integration/candidate-freeze.json'
        self.selection['effectiveParentAcceptance']=self.save('parent-acceptance-v2.json',self.current);self.save('parent-acceptance-selection.json',self.selection)
        with self.assertRaises(AssertionError):REVIEW.current_parent_acceptance()

if __name__=='__main__':unittest.main()
