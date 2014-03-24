/// ReceiveNetwork()
var n_id, t, t_buffer, command;

n_id = ds_map_find_value(async_load, "id");         
if n_id == global.server                                
{
  t = ds_map_find_value(async_load, "type");          
  if t == network_type_data
  {                                                   
    show_debug_message('got a packet!');
    t_buffer = ds_map_find_value(async_load, "buffer"); 
    command = buffer_read(t_buffer, buffer_u8);
    show_debug_message(string(command));
    if command==112 // 'p'
    {
      if !mic.visible
      {
        PlayClip();
      }
      else
      {
        global.queued=true;
      }
    }
    else if command==115 // 's'
    {
      Idle();
    }
  }
}
