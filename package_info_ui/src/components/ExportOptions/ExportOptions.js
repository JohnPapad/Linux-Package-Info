import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem } from 'reactstrap';

const ExportOptions = (props) => {

    return (
        <UncontrolledDropdown>
            <DropdownToggle caret color="primary">
                Export
            </DropdownToggle>
            <DropdownMenu right>
                <DropdownItem className="text-center" onClick={()=>props.exportHandler("CSV")}>
                    CSV
                </DropdownItem>
                <DropdownItem divider/>
                <DropdownItem className="text-center" onClick={()=>props.exportHandler("JSON")}>
                    JSON
                </DropdownItem>
            </DropdownMenu>
        </UncontrolledDropdown>
    );
}

export default ExportOptions;