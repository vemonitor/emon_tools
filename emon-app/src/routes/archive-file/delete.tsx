import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { idSchemeIn, idSchemeOut } from "@/lib/comon-schemas";
import { Link, useNavigate, useParams } from "react-router";


function DeleteArchiveFile() {
  const { fetchWithAuth } = useAuth();
  const { file_id } = useParams();
  const navigate = useNavigate();
  
  idSchemeIn.parse(file_id);
  const itemId = file_id ? parseInt(file_id) : 0
  idSchemeOut.parse(itemId);
  const DeleteArchiveFileAction = async () => {
    if(!itemId || itemId <= 0){
      return new Error(
        "Unable to delete Item, id is invalid"
      )
    }
    try {
      const response = await fetchWithAuth(
        `/api/v1/archive_file/delete/${itemId}/`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      ).then((response) => response.json())
      if (!response.success) {
        return {
          success: false,
          msg: response.msg,
          errors: response.errors,
          from_error: response.from_error,
        }
      }
    } catch (error: unknown) {
      console.log('Error fetching data:', error);
      return {
        success: false,
        msg: 'Unable to save data, please control all fields',
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
    navigate("/archive-file")
    return;
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Delete Item: Are you absolutely sure?</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="">
          This action cannot be undone. This will permanently delete this item
          and remove your data from our servers.
        </div>
        <Button
          variant="destructive"
          onClick={DeleteArchiveFileAction}
        >
          Delete
        </Button>
        <Button variant="ghost">
          <Link to="/archive-file">Back</Link>
        </Button>
      </CardContent>
    </Card>
  )
}

export default DeleteArchiveFile