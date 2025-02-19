def test_elastic(mock_vasp, clean_dir, si_structure):
    import numpy as np
    from jobflow import run_locally
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    from atomate2.common.schemas.elastic import ElasticDocument
    from atomate2.vasp.flows.elastic import ElasticMaker
    from atomate2.vasp.powerups import (
        update_user_incar_settings,
        update_user_kpoints_settings,
    )

    # mapping from job name to directory containing test files
    ref_paths = {
        "elastic relax 1/6": "Si_elastic/elastic_relax_1_6",
        "elastic relax 2/6": "Si_elastic/elastic_relax_2_6",
        "elastic relax 3/6": "Si_elastic/elastic_relax_3_6",
        "elastic relax 4/6": "Si_elastic/elastic_relax_4_6",
        "elastic relax 5/6": "Si_elastic/elastic_relax_5_6",
        "elastic relax 6/6": "Si_elastic/elastic_relax_6_6",
        "tight relax 1": "Si_elastic/tight_relax_1",
        "tight relax 2": "Si_elastic/tight_relax_2",
    }

    # settings passed to fake_run_vasp; adjust these to check for certain INCAR settings
    fake_run_vasp_kwargs = {
        "elastic relax 1/6": {"incar_settings": ["NSW", "ISMEAR", "ISIF"]},
        "elastic relax 2/6": {"incar_settings": ["NSW", "ISMEAR", "ISIF"]},
        "elastic relax 3/6": {"incar_settings": ["NSW", "ISMEAR", "ISIF"]},
        "elastic relax 4/6": {"incar_settings": ["NSW", "ISMEAR", "ISIF"]},
        "elastic relax 5/6": {"incar_settings": ["NSW", "ISMEAR", "ISIF"]},
        "elastic relax 6/6": {"incar_settings": ["NSW", "ISMEAR", "ISIF"]},
        "tight relax 1": {"incar_settings": ["NSW", "ISMEAR"]},
        "tight relax 2": {"incar_settings": ["NSW", "ISMEAR"]},
    }

    # automatically use fake VASP and write POTCAR.spec during the test
    mock_vasp(ref_paths, fake_run_vasp_kwargs)

    # generate flow
    si_prim = SpacegroupAnalyzer(si_structure).get_primitive_standard_structure()
    flow = ElasticMaker().make(si_prim)
    flow = update_user_kpoints_settings(
        flow, {"grid_density": 100}, name_filter="relax"
    )
    flow = update_user_incar_settings(flow, {"KSPACING": None}, name_filter="relax")

    # Run the flow or job and ensure that it finished running successfully
    responses = run_locally(flow, create_folders=True, ensure_success=True)

    # validation on the outputs
    elastic_output = responses[flow.jobs[-1].uuid][1].output
    assert isinstance(elastic_output, ElasticDocument)
    assert np.allclose(
        elastic_output.elastic_tensor.ieee_format,
        [
            [155.7923, 54.8871, 54.8871, 0.0, 0.0, 0.0],
            [54.8871, 155.7923, 54.8871, 0.0, 0.0, 0.0],
            [54.8871, 54.8871, 155.7923, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 94.6712, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 94.6712, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 94.6712],
        ],
        atol=1e-3,
    )
