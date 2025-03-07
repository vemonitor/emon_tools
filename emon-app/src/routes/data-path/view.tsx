import Pane from "@/components/layout/pane";
import { useAuth } from "@/hooks/use-auth";
import { useEffect } from "react";
import { useNavigate, useParams } from "react-router";
import { DataViewerList } from "../data-viewer/finaFilesViever";
import { ChartPane } from "../data-viewer/finaChartViever";

function ViewDataPath() {
  const { path_id } = useParams();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);
  return (
    <Pane
      title='Fina Reader'
      classBody={'h-full'}
    >

      <div className='grid grid-cols-8 h-full'>
        <div className='col-span-2 h-full'>
          <DataViewerList
            path_id={(path_id) ?? 0}
          />
        </div>
        <div className='col-span-6 h-full'>
          <ChartPane
            source={path_id ?? 'archive'}
            classBody='h-full'
          />
        </div>
      </div>
    </Pane>
  )
}

export default ViewDataPath