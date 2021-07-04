import { Button } from 'reactstrap';

const ExportOptions = (props) => {

    return (
        <span>
            <Button onClick={()=>props.exportHandler("CSV")} color="primary">
                Export to CSV
            </Button>
            <Button className="mx-4" onClick={()=>props.exportHandler("JSON")} color="primary">
                Export to JSON
            </Button>
        </span>
       
    );
}

export default ExportOptions;