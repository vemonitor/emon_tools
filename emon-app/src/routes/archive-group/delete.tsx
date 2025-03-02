import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { MouseEvent, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { z } from 'zod';


const idSchemeIn = z.string()
  .min(1)
  .max(9)
  .regex(/^[0-9]+$/, {
    message: 'Please enter a valid attribute (Only Alphabetical characters with accents and spaces are accepted)',
  })

const idSchemeOut = z.number()
  .positive();

function DeleteArchiveGroup() {
  const { isAuthenticated, fetchWithAuth } = useAuth();
  const { item_id } = useParams();
  const navigate = useNavigate();
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);
  idSchemeIn.parse(item_id);
  const itemId = item_id ? parseInt(item_id) : 0
  idSchemeOut.parse(itemId);
  const DeleteArchiveGroupAction = async (e: MouseEvent<HTMLButtonElement>) => {
    if(!itemId || itemId <= 0){
      return new Error(
        "Unable to delete Item, id is invalid"
      )
    }
    try {
      const response = await fetchWithAuth(
        `http://127.0.0.1:8000/api/v1/archive_group/delete/${itemId}/`,
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
    navigate("/archive-group")
    return;
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Delete Item: Are you absolutely sure?</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="">
          This action cannot be undone. This will permanently delete your account
          and remove your data from our servers.
        </div>
        <Button
          variant="destructive"
          onClick={DeleteArchiveGroupAction}
        >
          Delete
        </Button>
        <Button variant="ghost">
          <Link to="/archive-group">Back</Link>
        </Button>
      </CardContent>
    </Card>
  )
}

export default DeleteArchiveGroup