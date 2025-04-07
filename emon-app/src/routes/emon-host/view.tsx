import { validateSlug } from "@/lib/utils";
import { useParams } from "react-router";
import { HostedViewer } from "../graph-feed/hostedViewer";

function ViewEmonHost() {
  const { host_slug } = useParams();
  const slug = validateSlug(host_slug) 
  return (
    <HostedViewer
      slug={slug}
    />
  )
  }
  
  export default ViewEmonHost