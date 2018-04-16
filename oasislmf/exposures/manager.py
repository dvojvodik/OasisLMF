# -*- coding: utf-8 -*-

__all__ = [
    'OasisExposuresManagerInterface',
    'OasisExposuresManager'
]

import io
import itertools
import json
import logging
import os
import shutil

import pandas as pd
import six

from interface import Interface, implements

from ..keys.lookup import OasisKeysLookupFactory
from ..utils.exceptions import OasisException
from ..utils.values import get_utctimestamp
from ..models import OasisModel
from .pipeline import OasisFilesPipeline
from .csv_trans import Translator


class OasisExposuresManagerInterface(Interface):  # pragma: no cover
    """
    Interface class form managing a collection of exposures.

    :param oasis_models: A list of Oasis model objects with resources provided in the model objects'
        resources dictionaries.
    :type oasis_models: ``list(OasisModel)``
    """

    def __init__(self, oasis_models=None):
        """
        Class constructor.
        """
        pass

    def add_model(self, oasis_model):
        """
        Adds Oasis model object to the manager and sets up its resources.
        """
        pass

    def delete_model(self, oasis_model):
        """
        Deletes an existing Oasis model object in the manager.
        """
        pass

    def transform_source_to_canonical(self, oasis_model=None, **kwargs):
        """
        Transforms a source exposures/locations for a given ``oasis_model``
        object to a canonical/standard Oasis format.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.

        The transform is generic by default, but could be supplier specific if
        required.
        """
        pass

    def transform_canonical_to_model(self, oasis_model=None, **kwargs):
        """
        Transforms the canonical exposures/locations for a given ``oasis_model``
        object to a format suitable for an Oasis model keys lookup service.

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.
        """
        pass

    def get_keys(self, oasis_model=None, **kwargs):
        """
        Generates the Oasis keys and keys error files for a given model object.
        The keys file is a CSV file containing keys lookup information for
        locations with successful lookups, and has the following headers::

            LocID,PerilID,CoverageID,AreaPerilID,VulnerabilityID

        while the keys error file is a CSV file containing keys lookup
        information for locations with unsuccessful lookups (failures,
        no matches) and has the following headers::

            LocID,PerilID,CoverageID,Message

        All the required resources must be provided either in the model object
        resources dict or the ``kwargs`` dict.

        It is up to the specific implementation of this class of how these
        resources will be named in ``kwargs`` and how they will be used to
        effect the transformation.

        A "standard" implementation should use the lookup service factory
        class in ``oasis_utils`` (a submodule of `omdk`) namely

            ``oasis_utils.oasis_keys_lookup_service_utils.KeysLookupServiceFactory``
        """
        pass

    def load_canonical_exposures_profile(self, oasis_model=None, **kwargs):
        """
        Loads a JSON string or JSON file representation of the canonical
        exposures profile for a given ``oasis_model``, stores this in the
        model object's resources dict, and returns the object.
        """
        pass

    def load_canonical_account_profile(self, oasis_model=None, **kwargs):
        """
        Loads a JSON string or JSON file representation of the canonical
        account profile for a given ``oasis_model``, stores this in the
        model object's resources dict, and returns the object.
        """
        pass

    def generate_gul_files(self, oasis_model=None, **kwargs):
        """
        Generates Oasis GUL files.

        The required resources must be provided either via the model object
        resources dict or ``kwargs``.
        """

    def generate_fm_files(self, oasis_model=None, **kwargs):
        """
        Generates Oasis FM files.

        The required resources must be provided either via the model object
        resources dict or ``kwargs``.
        """

    def generate_oasis_files(self, oasis_model=None, include_fm=False, **kwargs):
        """
        Generates the full set of Oasis files, which should be GUL + FM + any extras

        The required resources must be provided either via the model object
        resources dict or ``kwargs``.
        """
        pass

    def create(self, model_supplier_id, model_id, model_version_id, resources=None):
        """
        Creates and returns an Oasis model with the provisioned resources if
        a resources dict was provided.
        """
        pass


class OasisExposuresManager(implements(OasisExposuresManagerInterface)):

    def __init__(self, oasis_models=None):
        self.logger = logging.getLogger()

        self.logger.debug('Exposures manager {} initialising'.format(self))

        self.logger.debug('Adding models')
        self._models = {}

        self.add_models(oasis_models)

        self.logger.debug('Exposures manager {} finished initialising'.format(self))

    def add_model(self, oasis_model):
        """
        Adds model to the manager and sets up its resources.
        """
        self._models[oasis_model.key] = oasis_model

        return oasis_model

    def add_models(self, oasis_models):
        """
        Adds a list of Oasis model objects to the manager.
        """
        for model in oasis_models or []:
            self.add_model(model)

    def delete_model(self, oasis_model):
        """
        Deletes an existing Oasis model object in the manager.
        """
        if oasis_model.key in self._models:
            oasis_model.resources['oasis_files_pipeline'].clear()

            del self._models[oasis_model.key]

    def delete_models(self, oasis_models):
        """
        Deletes a list of existing Oasis model objects in the manager.
        """
        for model in oasis_models:
            self.delete_model(model)

    @property
    def keys_lookup_factory(self):
        """
        Keys lookup service factory property - getter only.

            :getter: Gets the current keys lookup service factory instance
        """
        return self._keys_lookup_factory

    @property
    def models(self):
        """
        Model objects dictionary property.

            :getter: Gets the model in the models dict using the optional
                     ``key`` argument. If ``key`` is not given then the dict
                     is returned.

            :setter: Sets the value of the optional ``key`` in the models dict
                     to ``val`` where ``val`` is assumed to be an Oasis model
                     object (``omdk.OasisModel.OasisModel``).

                     If no ``key`` is given then ``val`` is assumed to be a new
                     models dict and is used to replace the existing dict.

            :deleter: Deletes the value of the optional ``key`` in the models
                      dict. If no ``key`` is given then the entire existing
                      dict is cleared.
        """
        return self._models

    @models.setter
    def models(self, val):
        self._models.clear()
        self._models.update(val)

    @models.deleter
    def models(self):
        self._models.clear()

    def transform_source_to_canonical(self, oasis_model=None, source_type='exposures', **kwargs):
        """
        Transforms a canonical exposures/locations file for a given
        ``oasis_model`` object to a canonical/standard Oasis format.

        It can also transform a source account file to a canonical account
        file, if the optional argument ``source_type`` has the value of ``account``.
        The default ``source_type`` is ``exposures``.

        By default parameters supplied to this function fill be used if present
        otherwise they will be taken from the `oasis_model` resources dictionary
        if the model is supplied.

        :param oasis_model: An optional Oasis model object
        :type oasis_model: ``oasislmf.models.model.OasisModel``

        :param source_exposures_file_path: Source exposures file path (if ``source_type`` is ``exposures``)
        :type source_exposures_file_path: str

        :param source_exposures_validation_file_path: Source exposures validation file (if ``source_type`` is ``exposures``)
        :type source_exposures_validation_file_path: str

        :param source_to_canonical_exposures_transformation_file_path: Source exposures transformation file (if ``source_type`` is ``exposures``)
        :type source_to_canonical_exposures_transformation_file_path: str

        :param canonical_exposures_file_path: Path to the output canonical exposure file (if ``source_type`` is ``exposures``)
        :type canonical_exposures_file_path: str

        :param source_account_file_path: Source account file path (if ``source_type`` is ``account``)
        :type source_exposures_file_path: str

        :param source_account_validation_file_path: Source account validation file (if ``source_type`` is ``account``)
        :type source_exposures_validation_file_path: str

        :param source_to_canonical_account_transformation_file_path: Source account transformation file (if ``source_type`` is ``account``)
        :type source_to_canonical_account_transformation_file_path: str

        :param canonical_account_file_path: Path to the output canonical account file (if ``source_type`` is ``account``)
        :type canonical_account_file_path: str

        :return: The path to the output canonical file
        """
        kwargs = self._process_default_kwargs(oasis_model=oasis_model, **kwargs)

        input_file_path = os.path.abspath(kwargs['source_account_file_path']) if source_type == 'account' else os.path.abspath(kwargs['source_exposures_file_path'])
        validation_file_path = os.path.abspath(kwargs['source_account_validation_file_path']) if source_type == 'account' else os.path.abspath(kwargs['source_exposures_validation_file_path'])
        transformation_file_path = os.path.abspath(kwargs['source_to_canonical_account_transformation_file_path']) if source_type == 'account' else os.path.abspath(kwargs['source_to_canonical_exposures_transformation_file_path'])
        output_file_path = os.path.abspath(kwargs['canonical_account_file_path']) if source_type == 'account' else os.path.abspath(kwargs['canonical_exposures_file_path'])

        translator = Translator(input_file_path, output_file_path, validation_file_path, transformation_file_path, append_row_nums=True)
        translator()

        if oasis_model:
            if source_type == 'account':
                oasis_model.resources['oasis_files_pipeline'].canonical_account_file_path = output_file_path
            else:
                oasis_model.resources['oasis_files_pipeline'].canonical_exposures_file_path = output_file_path

        return output_file_path

    def transform_canonical_to_model(self, oasis_model=None, **kwargs):
        """
        Transforms the canonical exposures/locations file for a given
        ``oasis_model`` object to a format suitable for an Oasis model keys
        lookup service.

        By default parameters supplied to this function fill be used if present
        otherwise they will be taken from the `oasis_model` resources dictionary
        if the model is supplied.

        :param oasis_model: The model to get keys for
        :type oasis_model: ``oasislmf.models.model.OasisModel``

        :param canonical_exposures_file_path: Path to the canonical exposures file
        :type canonical_exposures_file_path: str

        :param canonical_exposures_validation_file_path: Path to the exposure validation file
        :type canonical_exposures_validation_file_path: str

        :param canonical_to_model_exposures_transformation_file_path: Path to the exposure transformation file
        :type canonical_to_model_exposures_transformation_file_path: str

        :param model_exposures_file_path: Path to the output model exposure file
        :type model_exposures_file_path: str

        :return: The path to the output model exposure file
        """
        kwargs = self._process_default_kwargs(oasis_model=oasis_model, **kwargs)

        input_file_path = os.path.abspath(kwargs['canonical_exposures_file_path'])
        validation_file_path = os.path.abspath(kwargs['canonical_exposures_validation_file_path'])
        transformation_file_path = os.path.abspath(kwargs['canonical_to_model_exposures_transformation_file_path'])
        output_file_path = os.path.abspath(kwargs['model_exposures_file_path'])

        translator = Translator(input_file_path, output_file_path, validation_file_path, transformation_file_path, append_row_nums=False)
        translator()

        if oasis_model:
            oasis_model.resources['oasis_files_pipeline'].model_exposures_file_path = output_file_path

        return output_file_path

    def load_canonical_exposures_profile(
            self,
            oasis_model=None,
            canonical_exposures_profile_json=None,
            canonical_exposures_profile_json_path=None,
            **kwargs
        ):
        """
        Loads a JSON string or JSON file representation of the canonical
        exposures profile for a given ``oasis_model``, stores this in the
        model object's resources dict, and returns the object.
        """
        if oasis_model:
            canonical_exposures_profile_json = canonical_exposures_profile_json or oasis_model.resources.get('canonical_exposures_profile_json')
            canonical_exposures_profile_json_path = canonical_exposures_profile_json_path or oasis_model.resources.get('canonical_exposures_profile_json_path')

        profile = {}
        if canonical_exposures_profile_json:
            profile = json.loads(canonical_exposures_profile_json)
        elif canonical_exposures_profile_json_path:
            with io.open(canonical_exposures_profile_json_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)

        if oasis_model:
            oasis_model.resources['canonical_exposures_profile'] = profile

        return profile

    def load_canonical_account_profile(
            self,
            oasis_model=None,
            canonical_account_profile_json=None,
            canonical_account_profile_json_path=None,
            **kwargs
        ):
        """
        Loads a JSON string or JSON file representation of the canonical
        exposures profile for a given ``oasis_model``, stores this in the
        model object's resources dict, and returns the object.
        """
        if oasis_model:
            canonical_account_profile_json = canonical_account_profile_json or oasis_model.resources.get('canonical_account_profile_json')
            canonical_account_profile_json_path = canonical_account_profile_json_path or oasis_model.resources.get('canonical_account_profile_json_path')

        profile = {}
        if canonical_account_profile_json:
            profile = json.loads(canonical_account_profile_json)
        elif canonical_account_profile_json_path:
            with io.open(canonical_account_profile_json_path, 'r', encoding='utf-8') as f:
                profile = json.load(f)

        if oasis_model:
            oasis_model.resources['canonical_account_profile'] = profile

        return profile

    def get_keys(self, oasis_model=None, model_exposures_file_path=None, lookup=None, keys_file_path=None, keys_errors_file_path=None, **kwargs):
        """
        Generates the Oasis keys and keys error files for a given model object.
        The keys file is a CSV file containing keys lookup information for
        locations with successful lookups, and has the following headers::

            LocID,PerilID,CoverageID,AreaPerilID,VulnerabilityID

        while the keys error file is a CSV file containing keys lookup
        information for locations with unsuccessful lookups (failures,
        no matches) and has the following headers::

            LocID,PerilID,CoverageID,Message

        By default it is assumed that all the resources required for the
        transformation are present in the model object's resources dict,
        if the model is supplied. These can be overridden by providing the
        relevant optional parameters.

        If no model is supplied then the optional paramenters must be
        supplied.

        If the model is supplied the result key file path is stored in the
        models ``file_pipeline.keyfile_path`` property.

        :param oasis_model: The model to get keys for
        :type oasis_model: ``OasisModel``

        :param keys_file_path: Path to the keys file, required if ``oasis_model`` is ``None``
        :type keys_file_path: str

        :param keys_errors_file_path: Path to the keys error file, required if ``oasis_model`` is ``None``
        :type keys_errors_file_path: str

        :param lookup: Path to the keys lookup service to use, required if ``oasis_model`` is ``None``
        :type lookup: str

        :param model_exposures_file_path: Path to the exposures file, required if ``oasis_model`` is ``None``
        :type model_exposures_file_path: str

        :return: The path to the generated keys file
        """
        if oasis_model:
            _model_exposures_file_path = model_exposures_file_path or oasis_model.resources['oasis_files_pipeline'].model_exposures_file_path
            _lookup = lookup or oasis_model.resources.get('lookup')
            _keys_file_path = keys_file_path or oasis_model.resources['oasis_files_pipeline'].keys_file_path
            _keys_errors_file_path = keys_errors_file_path or oasis_model.resources['oasis_files_pipeline'].keys_errors_file_path

        _model_exposures_file_path, _keys_file_path, _keys_errors_file_path = map(
            lambda p: os.path.abspath(p) if p and not os.path.isabs(p) else p,
            [_model_exposures_file_path, _keys_file_path, _keys_errors_file_path]
        )

        _keys_file_path, _, _keys_errors_file_path, _ = OasisKeysLookupFactory().save_keys(
            keys_file_path=_keys_file_path,
            keys_errors_file_path=_keys_errors_file_path,
            lookup=_lookup,
            model_exposures_file_path=_model_exposures_file_path,
        )

        if oasis_model:
            oasis_model.resources['oasis_files_pipeline'].keys_file_path = _keys_file_path
            oasis_model.resources['oasis_files_pipeline'].keys_errors_file_path = _keys_errors_file_path

        return _keys_file_path, _keys_errors_file_path

    def _process_default_kwargs(self, oasis_model=None, **kwargs):
        if oasis_model:
            kwargs.setdefault('source_exposures_file_path', oasis_model.resources.get('source_exposures_file_path'))
            kwargs.setdefault('source_account_file_path', oasis_model.resources.get('source_account_file_path'))
            kwargs.setdefault('source_exposures_validation_file_path', oasis_model.resources.get('source_exposures_validation_file_path'))
            kwargs.setdefault('source_to_canonical_exposures_transformation_file_path', oasis_model.resources.get('source_to_canonical_exposures_transformation_file_path'))
            kwargs.setdefault('canonical_exposures_profile', oasis_model.resources.get('canonical_exposures_profile'))
            kwargs.setdefault('canonical_exposures_profile_json', oasis_model.resources.get('canonical_exposures_profile_json'))
            kwargs.setdefault('canonical_exposures_profile_json_path', oasis_model.resources.get('canonical_exposures_profile_json_path'))
            kwargs.setdefault('canonical_account_profile', oasis_model.resources.get('canonical_account_profile'))
            kwargs.setdefault('canonical_account_profile_json', oasis_model.resources.get('canonical_account_profile_json'))
            kwargs.setdefault('canonical_account_profile_json_path', oasis_model.resources.get('canonical_account_profile_json_path'))
            kwargs.setdefault('canonical_account_file_path', oasis_model.resources['oasis_files_pipeline'].canonical_account_file_path)
            kwargs.setdefault('canonical_exposures_file_path', oasis_model.resources['oasis_files_pipeline'].canonical_exposures_file_path)
            kwargs.setdefault('canonical_exposures_validation_file_path', oasis_model.resources.get('canonical_exposures_validation_file_path'))
            kwargs.setdefault('canonical_to_model_exposures_transformation_file_path', oasis_model.resources.get('canonical_to_model_exposures_transformation_file_path'))
            kwargs.setdefault('model_exposures_file_path', oasis_model.resources['oasis_files_pipeline'].model_exposures_file_path)
            kwargs.setdefault('keys_file_path', oasis_model.resources['oasis_files_pipeline'].keys_file_path)
            kwargs.setdefault('keys_errors_file_path', oasis_model.resources['oasis_files_pipeline'].keys_errors_file_path)
            kwargs.setdefault('items_file_path', oasis_model.resources['oasis_files_pipeline'].items_file_path)
            kwargs.setdefault('coverages_file_path', oasis_model.resources['oasis_files_pipeline'].coverages_file_path)
            kwargs.setdefault('gulsummaryxref_file_path', oasis_model.resources['oasis_files_pipeline'].gulsummaryxref_file_path)
            kwargs.setdefault('fm_policytc_file_path', oasis_model.resources['oasis_files_pipeline'].fm_policytc_file_path)
            kwargs.setdefault('fm_profile_file_path', oasis_model.resources['oasis_files_pipeline'].fm_profile_file_path)
            kwargs.setdefault('fm_policytc_file_path', oasis_model.resources['oasis_files_pipeline'].fm_programme_file_path)
            kwargs.setdefault('fm_xref_file_path', oasis_model.resources['oasis_files_pipeline'].fm_xref_file_path)
            kwargs.setdefault('fmsummaryxref_file_path', oasis_model.resources['oasis_files_pipeline'].fmsummaryxref_file_path)

        if not kwargs.get('canonical_exposures_profile'):
            kwargs['canonical_exposures_profile'] = self.load_canonical_exposures_profile(
                oasis_model=oasis_model,
                canonical_exposures_profile_json=kwargs.get('canonical_exposures_profile_json'),
                canonical_exposures_profile_json_path=kwargs.get('canonical_exposures_profile_json_path'),
            )

        if kwargs.get('include_fm') and not kwargs.get('canonical_account_profile'):
            kwargs['canonical_account_profile'] = self.load_canonical_account_profile(
                oasis_model=oasis_model,
                canonical_account_profile_json=kwargs.get('canonical_account_profile_json'),
                canonical_account_profile_json_path=kwargs.get('canonical_account_profile_json_path'),
            )

        return kwargs

    def load_exposure_master_data_frame(self, canonical_exposures_file_path, keys_file_path, canonical_exposures_profile, **kwargs):
        with io.open(canonical_exposures_file_path, 'r', encoding='utf-8') as cf:
            canexp_df = pd.read_csv(cf, float_precision='high')
            canexp_df = canexp_df.where(canexp_df.notnull(), None)
            canexp_df.columns = canexp_df.columns.str.lower()

        with io.open(keys_file_path, 'r', encoding='utf-8') as kf:
            keys_df = pd.read_csv(kf, float_precision='high')
            keys_df = keys_df.rename(columns={'CoverageID': 'CoverageType'})
            keys_df = keys_df.where(keys_df.notnull(), None)
            keys_df.columns = keys_df.columns.str.lower()

        tiv_fields = sorted(
            filter(lambda v: v.get('FieldName') == 'TIV', six.itervalues(canonical_exposures_profile))
        )

        columns = [
            'item_id',
            'canloc_id',
            'coverage_id',
            'tiv',
            'areaperil_id',
            'vulnerability_id',
            'group_id',
            'summary_id',
            'summaryset_id'
        ]
        result = pd.DataFrame(columns=columns, dtype=object)

        for col in columns:
            result[col] = result[col].astype(int) if col != 'tiv' else result[col]

        item_id = 0
        for i in range(len(keys_df)):
            keys_item = keys_df.iloc[i]

            canexp_item = canexp_df[canexp_df['row_id'] == keys_item['locid']]

            if canexp_item.empty:
                raise OasisException(
                    "No matching canonical exposure item found in canonical exposures data frame for keys item {}.".format(keys_item)
                )

            canexp_item = canexp_item.iloc[0]

            tiv_field_matches = filter(lambda f: f['CoverageTypeID'] == keys_item['coveragetype'], tiv_fields)
            for tiv_field in tiv_field_matches:
                tiv_lookup = tiv_field['ProfileElementName'].lower()
                tiv_value = canexp_item[tiv_lookup]
                if tiv_value > 0:
                    item_id += 1
                    result = result.append([{
                        'item_id': item_id,
                        'canloc_id': canexp_item['row_id'],
                        'coverage_id': item_id,
                        'tiv': tiv_value,
                        'areaperil_id': keys_item['areaperilid'],
                        'vulnerability_id': keys_item['vulnerabilityid'],
                        'group_id': item_id,
                        'summary_id': 1,
                        'summaryset_id': 1,
                    }])

        return result
    
    def load_fm_master_data_frame(self, canonical_exposures_file_path, keys_file_path, items_file_path, canonical_exposures_profile, canonical_account_profile, **kwargs):

        exp_mdf = self.load_exposure_master_data_frame(canonical_exposures_file_path, keys_file_path, canonical_exposures_profile)

        with io.open(canonical_exposures_file_path, 'r', encoding='utf-8') as cf:
            canexp_df = pd.read_csv(cf, float_precision='high')
            canexp_df = canexp_df.where(canexp_df.notnull(), None)
            canexp_df.columns = canexp_df.columns.str.lower()
        
        columns = [
            'itemid', 'canlocid', 'levelid', 'layerid', 'aggid', 'policytcid', 'deductible',
            'limit', 'share', 'deductibletype', 'calcrule', 'tiv', 'fm_level'
        ]

        cep = canonical_exposures_profile
        cap = canonical_account_profile

        fm_term_fields = {
            fm_level.lower(): {
                gi['ProfileElementName'].lower(): gi for gi in list(g)
            } for fm_level, g in itertools.groupby(
                sorted(
                   [v for v in cep.values() + cap.values() if 'FMLevel' in v and v['FMTermType'].lower() in ['tiv', 'deductible', 'limit']], 
                    key=lambda d: d['FMLevelOrder']
                ),
                key=lambda f: f['FMLevel']
            )
        }

        fm_levels = sorted(fm_term_fields, key=lambda f: fm_term_fields[f].values()[0]['FMLevelOrder'])

        grouped_fm_term_fields = {
            fm_level: {
                k:{gi['FMTermType'].lower():gi for gi in list(g)} for k, g in itertools.groupby(sorted(fm_term_fields[fm_level].values(), key=lambda f: f['ProfileElementName']), key=lambda f: f['FMTermGroupID'])
            } for fm_level in fm_levels
        }

        preset_data = list(
            itertools.product(
                fm_levels,
                zip(list(exp_mdf.item_id.values), list(exp_mdf.canloc_id.values), list(exp_mdf.tiv.values)))
        )
        fm_data = [
            {
                k:v for k, v in zip(columns, [item_id,canloc_id,None,None, None,None,None,None,None,None,None,tiv,fm_level])
            } for fm_level, (item_id, canloc_id, tiv) in preset_data
        ]

        fm_df = pd.DataFrame(columns=columns, data=fm_data)

        for i in range(len(fm_df)):
            fm_item = fm_df.iloc[i]
            canexp_item = canexp_df[canexp_df['row_id'] == fm_item['canlocid']]

            if fm_item['fm_level'] == 'coverage':
                for gid in grouped_fm_term_fields['coverage']:
                    tiv_field_name = grouped_fm_term_fields['coverage'][gid]['tiv']['ProfileElementName'].lower()
                    if tiv_field_name in canexp_item and float(canexp_item[tiv_field_name]) == float(fm_item['tiv']):
                        limit_field_name = grouped_fm_term_fields['coverage'][gid]['limit']['ProfileElementName'].lower()
                        limit_val = float(canexp_item[limit_field_name])
                        fm_df.at[i,'limit'] = limit_val if limit_val > 1 else (limit_val * float(fm_item['tiv']))

                        ded_field_name = grouped_fm_term_fields['coverage'][gid]['deductible']['ProfileElementName'].lower()
                        ded_val = float(canexp_item[ded_field_name])
                        fm_df.at[i,'deductible'] = ded_val if ded_val > 1 else (ded_val * float(fm_item['tiv']))

                        ded_type = grouped_fm_term_fields['coverage'][gid]['deductible']['DeductibleType'] if 'DeductibleType' in grouped_fm_term_fields['coverage'][gid]['deductible'] else u'B'
                        fm_df.at[i,'deductibletype'] = ded_type

                        break
            else:
                limit_field_name = grouped_fm_term_fields[fm_item['fm_level']][1]['limit']['ProfileElementName'].lower() if 'limit' in grouped_fm_term_fields[fm_item['fm_level']][1] else None
                limit_val = float(canexp_item[limit_field_name]) if limit_field_name and limit_field_name in canexp_item else 0
                fm_df.at[i,'limit'] = limit_val if limit_val > 1 else (limit_val * float(fm_item['tiv']))

                ded_field_name = grouped_fm_term_fields[fm_item['fm_level']][1]['deductible']['ProfileElementName'].lower() if 'deductible' in grouped_fm_term_fields[fm_item['fm_level']][1] else None
                ded_val = float(canexp_item[ded_field_name]) if ded_field_name and ded_field_name in canexp_item else 0
                fm_df.at[i,'deductible'] = ded_val if ded_val > 1 else (ded_val * float(fm_item['tiv']))
                
                ded_type = grouped_fm_term_fields['coverage'][1]['deductible']['DeductibleType'] if 'DeductibleType' in grouped_fm_term_fields['coverage'][1]['deductible'] else u'B'
                fm_df.at[i,'deductibletype'] = ded_type

            share_prop_of_lim = 0   # temporary logic
            fm_df.at[i, 'share'] = share_prop_of_lim

            if limit_val == share_prop_of_lim == 0 and ded_type == 'B':
                calc_rule = 12
            elif limit_val == 0 and share_prop_of_lim > 0 and ded_type == 'B':
                calc_rule = 15
            elif limit_val > 0 and share_prop_of_lim == 0 and ded_type == 'B':
                calc_rule = 1
            elif ded_type == 'MI':
                calc_rule = 11
            elif ded_type == 'MA':
                calc_rule = 10
            else:
                calc_rule = 2

            fm_df.at[i, 'calcrule'] = calc_rule


    def _write_csvs(self, columns, data_frame, file_path):
        data_frame.to_csv(
            columns=columns,
            path_or_buf=file_path,
            encoding='utf-8',
            chunksize=1000,
            index=False
        )

    def generate_items_file(self, oasis_model=None, data_frame=None, **kwargs):
        """
        Generates an items file for the given ``oasis_model``.
        """
        kwargs = self._process_default_kwargs(oasis_model=oasis_model, **kwargs)

        if data_frame is None:
            data_frame = self.load_exposure_master_data_frame(**kwargs)

        self._write_csvs(
            ['item_id', 'coverage_id', 'areaperil_id', 'vulnerability_id', 'group_id'],
            data_frame,
            kwargs['items_file_path']
        )

        if oasis_model:
            oasis_model.resources['oasis_files_pipeline'].items_file_path = kwargs['items_file_path']

        return kwargs['items_file_path']

    def generate_coverages_file(self, oasis_model=None, data_frame=None, **kwargs):
        """
        Generates a coverages file for the given ``oasis_model``.
        """
        kwargs = self._process_default_kwargs(oasis_model=oasis_model, **kwargs)

        if data_frame is None:
            data_frame = self.load_exposure_master_data_frame(**kwargs)

        self._write_csvs(
            ['coverage_id', 'tiv'],
            data_frame,
            kwargs['coverages_file_path']
        )

        if oasis_model:
            oasis_model.resources['oasis_files_pipeline'].coverages_file = kwargs.get('coverages_file_path')

        return kwargs.get('coverages_file_path')

    def generate_gulsummaryxref_file(self, oasis_model=None, data_frame=None, **kwargs):
        """
        Generates a gulsummaryxref file for the given ``oasis_model``.
        """
        kwargs = self._process_default_kwargs(oasis_model=oasis_model, **kwargs)

        if data_frame is None:
            data_frame = self.load_exposure_master_data_frame(**kwargs)

        self._write_csvs(
            ['coverage_id', 'summary_id', 'summaryset_id'],
            data_frame,
            kwargs['gulsummaryxref_file_path']
        )

        if oasis_model:
            oasis_model.resources['oasis_files_pipeline'].gulsummaryxref_path = kwargs['gulsummaryxref_file_path']

        return kwargs['gulsummaryxref_file_path']

    def generate_fm_policytc_file(self, oasis_model=None, **kwargs):
        """
        Generates an FM policy T & C file for the given ``oasis_model``.
        """
        pass

    def generate_fm_profile_file(self, oasis_model=None, **kwargs):
        """
        Generates an FM profile file for the given ``oasis_model``.
        """
        pass

    def generate_fm_programme_file(self, oasis_model=None, **kwargs):
        """
        Generates a FM programme file for the given ``oasis_model``.
        """
        pass

    def generate_fm_xref_file(self, oasis_model=None, **kwargs):
        """
        Generates a FM xref file for the given ``oasis_model``.
        """
        pass

    def generate_fmsummaryxref_file(self, oasis_model=None, **kwargs):
        """
        Generates a FM summaryxref file for the given ``oasis_model``.
        """
        pass

    def generate_gul_files(self, oasis_model=None, **kwargs):
        """
        Generates the standard Oasis GUL files, namely::

            items.csv
            coverages.csv
            gulsummaryxref.csv
        """
        kwargs = self._process_default_kwargs(oasis_model=oasis_model, **kwargs)
        data_frame = self.load_exposure_master_data_frame(**kwargs)

        self.generate_items_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)
        self.generate_coverages_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)
        self.generate_gulsummaryxref_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)

        return {
            'items_file_path': kwargs['items_file_path'],
            'coverages_file_path': kwargs['coverages_file_path'],
            'gulsummaryxref_file_path': kwargs['gulsummaryxref_file_path']
        }

    def generate_fm_files(self, oasis_model=None, **kwargs):
        """
        Generate Oasis FM files, namely::

            fm_policytc.csv
            fm_profile.csv
            fm_programm.ecsv
            fm_xref.csv
            fm_summaryxref.csv
        """
        kwargs = self._process_default_kwargs(oasis_model=oasis_model, **kwargs)
        data_frame = self.load_fm_exposure_master_data_frame(**kwargs)

        self.generate_fm_policytc_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)
        self.generate_fm_profile_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)
        self.generate_fm_programme_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)
        self.generate_fm_xref_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)
        self.generate_fmsummaryxref_file(oasis_model=oasis_model, data_frame=data_frame, **kwargs)

        return {
            'fm_policytc_file_path': kwargs['fm_policytc_file_path'],
            'fm_profile_file_path': kwargs['fm_profile_file_path'],
            'fm_programme_file_path': kwargs['fm_programme_file_path'],
            'fm_xref_file_path': kwargs['fm_xref_file_path'],
            'fmsummaryxref_file_path': kwargs['fmsummaryxref_file_path']
        }

    def generate_oasis_files(self, oasis_model=None, include_fm=False, **kwargs):
        gul_files = self.generate_gul_files(oasis_model=oasis_model, **kwargs)

        if not include_fm:
            return gul_files

        fm_files = self.generate_fm_files(oasis_model=oasis_model, **kwargs)

        return {k:v for k, v in gul_files.items() + fm_files.items()}

    def clear_oasis_files_pipeline(self, oasis_model, **kwargs):
        """
        Clears the files pipeline for the given Oasis model object.

        Args:
            ``oasis_model`` (``omdk.models.OasisModel.OasisModel``): The model object.

            ``**kwargs`` (arbitary keyword arguments):

        Returns:
            ``oasis_model`` (``omdk.models.OasisModel.OasisModel``): The model object with its
            files pipeline cleared.
        """
        oasis_model.resources.get('oasis_files_pipeline').clear()

        return oasis_model

    def start_oasis_files_pipeline(
        self,
        oasis_model=None,
        oasis_files_path=None, 
        include_fm=False,
        source_exposures_file_path=None,
        source_account_file_path=None,
        logger=None
    ):
        """
        Starts the files pipeline for the given Oasis model object,
        which is the generation of the Oasis items, coverages and GUL summary
        files, and possibly the FM files, from the source exposures file,
        source account file, canonical exposures profile, and associated
        validation files and transformation files for the source and
        intermediate files (canonical exposures, model exposures).

        :param oasis_model: The Oasis model object
        :type oasis_model: `oasislmf.models.model.OasisModel`

        :param oasis_files_path: Path where generated Oasis files should be
                                 written
        :type oasis_files_path: str

        :param include_fm: Boolean indicating whether FM files should be
                           generated
        :param include_fm: bool

        :param source_exposures_file_path: Path to the source exposures file
        :type source_exposures_file_path: str

        :param source_account_file_path: Path to the source account file
        :type source_account_file_path: str

        :param logger: Logger object
        :type logger: `logging.Logger`
        """
        logger = logger or logging.getLogger()
        logger.info('\nChecking output files directory exists for model')

        if oasis_model and not oasis_files_path:
            oasis_files_path = oasis_model.resources.get('oasis_files_path')

        if not oasis_files_path:
            raise OasisException('No output directory provided.'.format(oasis_model))
        elif not os.path.exists(oasis_files_path):
            raise OasisException('Output directory {} does not exist on the filesystem.'.format(oasis_files_path))

        logger.info('\nChecking for source exposures file')
        if oasis_model and not source_exposures_file_path:
            source_exposures_file_path = oasis_model.resources.get('source_exposures_file_path')
        if not source_exposures_file_path:
            raise OasisException('No source exposures file path provided in arguments or model resources')
        elif not os.path.exists(source_exposures_file_path):
            raise OasisException("Source exposures file path {} does not exist on the filesysem.".format(source_exposures_file_path))

        if include_fm:
            logger.info('\nChecking for source account file')
            if oasis_model and not source_account_file_path:
                source_account_file_path = oasis_model.resources.get('source_account_file_path')
            if not source_account_file_path:
                raise OasisException('FM option indicated but no source account file path provided in arguments or model resources')
            elif not os.path.exists(source_account_file_path):
                raise OasisException("Source account file path {} does not exist on the filesysem.".format(source_account_file_path))

        utcnow = get_utctimestamp(fmt='%Y%m%d%H%M%S')
        kwargs = self._process_default_kwargs(
            oasis_model=oasis_model,
            include_fm=include_fm,
            source_exposures_file_path=source_exposures_file_path,
            source_account_file_path=source_account_file_path,
            canonical_exposures_file_path=os.path.join(oasis_files_path, 'canexp-{}.csv'.format(utcnow)),
            canonical_account_file_path=os.path.join(oasis_files_path, 'canacc-{}.csv'.format(utcnow)),
            model_exposures_file_path=os.path.join(oasis_files_path, 'modexp-{}.csv'.format(utcnow)),
            keys_file_path=os.path.join(oasis_files_path, 'oasiskeys-{}.csv'.format(utcnow)),
            keys_errors_file_path=os.path.join(oasis_files_path, 'oasiskeys-errors-{}.csv'.format(utcnow)),
            items_file_path=os.path.join(oasis_files_path, 'items.csv'),
            coverages_file_path=os.path.join(oasis_files_path, 'coverages.csv'),
            gulsummaryxref_file_path=os.path.join(oasis_files_path, 'gulsummaryxref.csv'),
            fm_policytc_file_path=os.path.join(oasis_files_path, 'fm_policytc.csv'),
            fm_profile_file_path=os.path.join(oasis_files_path, 'fm_profile.csv'),
            fm_programme_file_path=os.path.join(oasis_files_path, 'fm_programme.csv'),
            fm_xref_file_path=os.path.join(oasis_files_path, 'fm_xref.csv'),
            fmsummaryxref_file_path=os.path.join(oasis_files_path, 'fmsummaryxref.csv')
        )

        source_exposures_file_path = kwargs.get('source_exposures_file_path')
        if not os.path.exists(source_exposures_file_path):
            self.logger.info('\nCopying source exposures file to input files directory')
            shutil.copy2(source_exposures_file_path, oasis_files_path)

        if include_fm:
            source_account_file_path = kwargs.get('source_account_file_path')
            if not os.path.exists(source_exposures_file_path):
                self.logger.info('\nCopying source exposures file to input files directory')
                shutil.copy2(source_account_file_path, oasis_files_path)

        logger.info('\nGenerating canonical exposures file {canonical_exposures_file_path}'.format(**kwargs))
        self.transform_source_to_canonical(**kwargs)

        if include_fm:
            logger.info('\nGenerating canonical account file {canonical_account_file_path}'.format(**kwargs))
            self.transform_source_to_canonical(source_type='account', **kwargs)

        logger.info('\nGenerating model exposures file {model_exposures_file_path}'.format(**kwargs))
        self.transform_canonical_to_model(**kwargs)

        logger.info('\nGenerating keys file {keys_file_path} and keys errors file {keys_errors_file_path}'.format(**kwargs))
        self.get_keys(oasis_model=oasis_model, **kwargs)

        logger.info('\nGenerating Oasis files (exposures=True, FM files={})'.format(include_fm))
        return self.generate_oasis_files(oasis_model=oasis_model, include_fm=include_fm, **kwargs)

    def create(self, model_supplier_id, model_id, model_version_id, resources=None):
        model = OasisModel(
            model_supplier_id,
            model_id,
            model_version_id,
            resources=resources
        )

        # set default resources
        model.resources.setdefault('oasis_files_path', os.path.join('Files', model.key.replace('/', '-')))
        if not os.path.isabs(model.resources.get('oasis_files_path')):
            model.resources['oasis_files_path'] = os.path.abspath(model.resources['oasis_files_path'])

        model.resources.setdefault('oasis_files_pipeline', OasisFilesPipeline(model_key=model.key))
        if not isinstance(model.resources['oasis_files_pipeline'], OasisFilesPipeline):
            raise OasisException(
                'Oasis files pipeline object for model {} is not of type {}'.format(model, OasisFilesPipeline))

        if model.resources.get('canonical_exposures_profile') is None:
            self.load_canonical_exposures_profile(oasis_model=model)

        if (
            model.resources.get('canonical_account_profile_json_path') or
            model.resources.get('canonical_account_profile_json') or
            model.resources.get('canonical_account_profile')
        ) and model.get('source_account_file_path'):
            if model.resources.get('canonical_account_profile') is None:
                self.load_canonical_account_profile(oasis_model=model)

        self.add_model(model)

        return model
