import { useParams } from "react-router";
import { validateSlug } from "@/lib/utils";
import { FinaViewer } from "../graph-fina/finaViewer";

function ViewDataPath() {
  const { path_slug } = useParams();
  const slug = validateSlug(path_slug) 
  return (
    <FinaViewer
      slug={slug}
    />
  )
}

export default ViewDataPath