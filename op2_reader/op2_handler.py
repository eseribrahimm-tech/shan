from pyNastran.op2.op2 import OP2
from collections import defaultdict
import numpy as np


class Op2Handler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.op2 = None
        self.loadcases = {}
        self.result_types = defaultdict(dict)
        self.load()

    def load(self):
        try:
            self.op2 = OP2(self.file_path, debug=False)
            self._parse_results()
        except Exception as e:
            raise Exception(f"Op2 dosyası okunamadı: {str(e)}")

    def _parse_results(self):
        """Op2 dosyasındaki tüm sonuçları parse et"""
        if not self.op2:
            return

        # Displacement results
        if hasattr(self.op2, 'displacements') and self.op2.displacements:
            for subcase_id, displacement in self.op2.displacements.items():
                if subcase_id not in self.loadcases:
                    self.loadcases[subcase_id] = f"Loadcase {subcase_id}"
                self.result_types[subcase_id]['displacement'] = displacement

        # Stress results
        if hasattr(self.op2, 'stresses') and self.op2.stresses:
            for subcase_id, stress in self.op2.stresses.items():
                if subcase_id not in self.loadcases:
                    self.loadcases[subcase_id] = f"Loadcase {subcase_id}"
                self.result_types[subcase_id]['stress'] = stress

        # Strain results
        if hasattr(self.op2, 'strains') and self.op2.strains:
            for subcase_id, strain in self.op2.strains.items():
                if subcase_id not in self.loadcases:
                    self.loadcases[subcase_id] = f"Loadcase {subcase_id}"
                self.result_types[subcase_id]['strain'] = strain

        # Force results
        if hasattr(self.op2, 'forces') and self.op2.forces:
            for subcase_id, force in self.op2.forces.items():
                if subcase_id not in self.loadcases:
                    self.loadcases[subcase_id] = f"Loadcase {subcase_id}"
                self.result_types[subcase_id]['force'] = force

    def get_loadcases(self):
        """Tüm loadcase'leri döndür"""
        return self.loadcases

    def get_result_types(self, subcase_id):
        """Belirli subcase için mevcut result type'larını döndür"""
        return list(self.result_types.get(subcase_id, {}).keys())

    def get_node_results(self, subcase_id, node_id, result_type):
        """Belirli node için sonuçları getir"""
        results = {}

        if subcase_id not in self.result_types or result_type not in self.result_types[subcase_id]:
            return results

        obj = self.result_types[subcase_id][result_type]

        try:
            if result_type == 'displacement':
                data = obj.data
                if hasattr(obj, 'node_gridtype'):
                    node_index = np.where(obj.node_gridtype[:, 0] == node_id)[0]
                    if len(node_index) > 0:
                        idx = node_index[0]
                        if result_type == 'displacement' and data.shape[1] >= 6:
                            results = {
                                'T1': data[idx, 0],
                                'T2': data[idx, 1],
                                'T3': data[idx, 2],
                                'R1': data[idx, 3],
                                'R2': data[idx, 4],
                                'R3': data[idx, 5]
                            }
            elif result_type == 'stress' or result_type == 'strain':
                if hasattr(obj, 'node_gridtype') and hasattr(obj, 'data'):
                    node_index = np.where(obj.node_gridtype[:, 0] == node_id)[0]
                    if len(node_index) > 0:
                        data = obj.data[node_index]
                        for idx, d in enumerate(data):
                            results[f"Element_{idx}"] = d.tolist() if isinstance(d, np.ndarray) else d

            elif result_type == 'force':
                if hasattr(obj, 'node_gridtype') and hasattr(obj, 'data'):
                    node_index = np.where(obj.node_gridtype[:, 0] == node_id)[0]
                    if len(node_index) > 0:
                        data = obj.data[node_index]
                        for idx, d in enumerate(data):
                            results[f"Element_{idx}"] = d.tolist() if isinstance(d, np.ndarray) else d

        except Exception as e:
            results['error'] = str(e)

        return results

    def get_element_results(self, subcase_id, element_id, result_type):
        """Belirli element için sonuçları getir"""
        results = {}

        if subcase_id not in self.result_types or result_type not in self.result_types[subcase_id]:
            return results

        obj = self.result_types[subcase_id][result_type]

        try:
            if hasattr(obj, 'element_node') and hasattr(obj, 'data'):
                element_index = np.where(obj.element_node[:, 0] == element_id)[0]
                if len(element_index) > 0:
                    data = obj.data[element_index]
                    results['element_id'] = element_id
                    results['data'] = data.tolist() if isinstance(data, np.ndarray) else data

        except Exception as e:
            results['error'] = str(e)

        return results

    def get_all_node_ids(self):
        """Tüm node ID'lerini döndür"""
        node_ids = set()
        for subcase_results in self.result_types.values():
            for result_obj in subcase_results.values():
                if hasattr(result_obj, 'node_gridtype'):
                    node_ids.update(result_obj.node_gridtype[:, 0].astype(int))
        return sorted(list(node_ids))

    def get_all_element_ids(self):
        """Tüm element ID'lerini döndür"""
        element_ids = set()
        for subcase_results in self.result_types.values():
            for result_obj in subcase_results.values():
                if hasattr(result_obj, 'element_node'):
                    element_ids.update(result_obj.element_node[:, 0].astype(int))
        return sorted(list(element_ids))
