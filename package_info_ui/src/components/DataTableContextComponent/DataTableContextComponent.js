import { Component } from "react";
import { Row, Col, Container, Button, UncontrolledCollapse, List } from "reactstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileExport, faTrashAlt, faFileCsv, faFileCode, faFileDownload, faSortDown, faExclamationTriangle, faMinusSquare, faEraser } from '@fortawesome/free-solid-svg-icons';
import { downloadCSV } from '../../utilities/CSVutil';
import { downloadJSON } from '../../utilities/JSONutil';
import { API } from "../../services/API";


const DataTableContextComponent = (props) => {
    const { selectedPackages } = props.selectedPackagesInfo;
    const selectedPackagesOnlyOneDistro = props.selectedPackagesInfo.onlyOneDistro;
    console.log("selectedPackagessss", selectedPackages)
    console.log("selectedPackagesOnlyOneDistro", selectedPackagesOnlyOneDistro)
    if (selectedPackages.length === 0) return null;

    const createDockerfile = async () => {
        if (!selectedPackagesOnlyOneDistro) return;

        const [distro_name, distro_version] = selectedPackages[0].distro.split(":");
        const packages = selectedPackages.map(packageInfo=>{
            return {
                "name": packageInfo.name,
                "version": packageInfo.selectedVersion
            }
        });

        const payload = {
            distro_name,
            distro_version,
            "distro_type": selectedPackages[0].type,
            packages
        };

        console.log("dockerfile payload: ", payload)
        // return;
        const createdDockerfile = await API.getPackagesDockerfile(payload);
        console.log("dockerfile", createdDockerfile)

        const blob = new Blob([createdDockerfile], { type: 'text/plain' });
        const link = document.createElement('a');
        const filename = `${selectedPackages[0].distro}.Dockerfile`;
        console.log("filename", filename)

        link.setAttribute('href', window.URL.createObjectURL(blob));
        link.setAttribute('download', filename);
        link.click();
    }

    return(
        <Container fluid className="py-3" style={{backgroundColor: '#e3f2fd', text: 'rgba(0, 0, 0, 0.87)'}}>
            <Row>
                <Col>
                    <Button color="link" id="toggler" className="pb-0">
                        {
                            selectedPackages.length === 1 ?
                            "1 package has been selected" :
                            selectedPackages.length + " packages have been selected"
                        } 
                        <FontAwesomeIcon icon={faSortDown} className="ms-1 mb-1"/>
                    </Button>
                    <UncontrolledCollapse toggler="#toggler">
                        <List className="mb-0 mt-1">
                            {
                                selectedPackages.map(packageInfo=>(
                                    <li key={packageInfo.id}>
                                        <strong>{packageInfo.name}</strong>,{' '}
                                        {
                                            packageInfo.selectedVersion &&
                                            packageInfo.selectedVersion + ", "
                                        } 
                                        <i>{packageInfo.distro}</i>
                                        <FontAwesomeIcon role="button" onClick={()=>props.deselectedOneHandler(packageInfo.id)} icon={faMinusSquare} className="ms-2 text-warning"/>
                                    </li>
                                ))
                            }
                        </List>
                    </UncontrolledCollapse>
                </Col>
                <Col xs="auto" className="ml-auto">
                    <div>
                        <Button size="sm" onClick={props.deselectedAllHandler} color="warning" className='fw-bold'>
                            Deselect All
                            <FontAwesomeIcon icon={faTrashAlt} className="ms-2"/>
                        </Button>
                        <Button size="sm" onClick={createDockerfile} color="secondary" className='fw-bold mx-4'>
                            Export to Dockerfile
                            <FontAwesomeIcon icon={faFileDownload} className="ms-2"/>
                        </Button>
                        <Button size="sm" onClick={()=>downloadCSV(selectedPackages)} color="primary" className='fw-bold'>
                            Export to CSV
                            <FontAwesomeIcon icon={faFileCsv} className="ms-2"/>
                        </Button>
                        <Button size="sm" className="ms-2 me-1 fw-bold" onClick={()=>downloadJSON(selectedPackages)} color="primary">
                            Export to JSON
                            <FontAwesomeIcon icon={faFileCode} className="ms-2"/>
                        </Button>
                    </div>
                    {
                        (!selectedPackagesOnlyOneDistro) &&
                        <div className="pe-2 pt-2 text-danger">
                            <FontAwesomeIcon icon={faExclamationTriangle} className="me-1"/>
                            Packages from different distributions cannot be combined in the same Dockerfile
                        </div>
                    }
                </Col>
            </Row>
        </Container>
    );
}

export default DataTableContextComponent;