import System.Process
import Control.Concurrent (threadDelay)
import Control.DeepSeq
import System.Exit

main ::  IO()
main = do
  test

test :: IO()
test = do
  line <- getLine
  case head line of
    'r' -> do
      putStrLn "Recording..."
      r <- record "test.wav"
      r `deepseq` test
    'p' -> do
      putStrLn "Playing..."
      p <- play "test.wav"
      p `deepseq` test
    otherwise -> do
      putStrLn "Done."
      return ()

record :: String -> IO()
record filename = do
  let path = "C:\\Users\\Brandon\\PartyLine\\"
  process <- runCommand $ path ++ "rec " ++ filename
  delay <- threadDelay $ 10*1000
  delay `deepseq` (terminateProcess process)

play :: String -> IO()
play filename = do
  let path = "C:\\Users\\Brandon\\PartyLine\\"
  process <- runCommand $ path ++ "play " ++ filename
  wait <- waitForProcess process
  let success = exitToSuccess wait
  success `deepseq` (return ())

exitToSuccess :: ExitCode -> Bool
exitToSuccess ExitSuccess = True
exitToSuccess (ExitFailure _) = False
