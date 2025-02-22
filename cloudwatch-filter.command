fields ((@memorySize / 1073741824 ) * (@billedDuration / 1000) * 0.00001667) + 0.0000002 as costPerInvocation,
        @timestamp, @entity.KeyAttributes.Name,
        @billedDuration, (@memorySize/1073741824) as memorySized,
        (@maxMemoryUsed / 1073741824) as memUsed,
       (@billedDuration / 1000) as durationSec
| filter ispresent(@billedDuration)
| sort costPerInvocation desc