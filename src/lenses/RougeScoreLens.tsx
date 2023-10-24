
import { log } from "console";
import { Lens } from "../types";

const calculateRougeScore=(values: unknown[])=>{
    return values;
}

const RougeScoreLens: Lens = ({values, columns})=>{
    const result = calculateRougeScore(values)
    return (
        <>
            RougeScoreView: {result}
        </>
    )
}

RougeScoreLens.key="RougeScoreView"
RougeScoreLens.dataTypes=["str"]
RougeScoreLens.defaultHeight = 100
RougeScoreLens.minHeight=22
RougeScoreLens.maxHeight=100
RougeScoreLens.multi=true
RougeScoreLens.displayName="ROUGE Score"
RougeScoreLens.filterAllowedColumns=(allColumns, selectedColumns) => {
    // if(selectedColumns.length===2)
    //     return selectedColumns
    // else return []
    return []
};
export default RougeScoreLens